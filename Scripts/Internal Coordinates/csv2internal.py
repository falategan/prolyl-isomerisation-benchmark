import argparse
from pathlib import Path
from typing import IO
import numpy as np
import math
import csv
from xyz2internal import parse_query


ATOM_DICT = {
        "C1": 0,
        "C2": 1,
        "C3": 2,
        "C4": 3,
        "C5": 4,
        "C6": 5,
        "C7": 6,
        "C8": 7,
        "N1": 22,
        "N2": 23,
        "O1": 24,
        "O2": 25
        }


class Residue:
    def __init__(self, csv_entry: dict[str, float]):
        self.pdb_id = csv_entry.pop("PDB ID")
        self.chain_id = csv_entry.pop("Chain ID")
        self.residue_index = csv_entry.pop("Residue Index")
        self.altloc = csv_entry.pop("AltLoc")
        self.insertion_code = csv_entry.pop("Insertion Code")
        self.subsequent_residue = csv_entry.pop("Subsequent Residue")

        self.atoms = dict()
        coordinates = dict()
        for key, value in csv_entry.items():
            atom, coordinate = key.split(".")
            if coordinate in "xyz":
                if atom not in coordinates:
                    coordinates[atom] = dict()
                coordinates[atom][coordinate] = float(value)
            else:
                print(f"Invalid coordinate {coordinate}")
        for atom_name, vector in coordinates.items():
            self.atoms[ATOM_DICT[atom_name]] = Atom(
                residue=self,
                index=ATOM_DICT[atom_name],
                atom_type=atom_name,
                x=vector["x"],
                y=vector["y"],
                z=vector["z"]
                )
    
    def __str__(self) -> str:
        string = f"Residue {self.index}\n"
        for index, atom in self.atoms.items():
            string += f"{index}\t{atom.atom_type}\t{atom.position_vector}\n"
        return string
    
    def __getitem__(self, key):
        return self.atoms[key]
            


class Atom:
    def __init__(
            self,
            residue: Residue,
            index: int,
            atom_type: str,
            x: float,
            y: float,
            z: float
            ):
        self.residue = residue
        self.index = index
        self.atom_type = atom_type
        self.position_vector = np.array([x, y, z])
    
    def x(self) -> int:
        return self.position_vector[0]
    
    def y(self) -> int:
        return self.position_vector[1]
    
    def z(self) -> int:
        return self.position_vector[2]
    
    def __str__(self):
        return f"{self.index}\t{self.atom_type}\t{self.position_vector}"
    

def get_args() -> [dict]:
    parser = argparse.ArgumentParser(
        prog="csv_to_internal_coords",
        description="reads csv file and returns the internal "
                    "coordinates of each residue in csv format"
        )
    parser.add_argument("input-file-path")
    parser.add_argument("query-file-path")
    parser.add_argument("output-file-path")
    return vars(parser.parse_args())


def read_residues(file: IO):
    residue_reader = csv.DictReader(file)
    for i, row in enumerate(residue_reader):
        yield Residue(row)
        
        
def distance(atom_1, atom_2):
    distance = np.linalg.norm(
        atom_2.position_vector - atom_1.position_vector
        )
    return distance


def get_lengths(
        entry: Residue,
        length_query: dict[str: tuple[int, int]]
        ) -> dict[str: float]:
    lengths = {}
    for name, pair in length_query.items():
        atom_1 = entry[pair[0]]
        atom_2 = entry[pair[1]]
        lengths[name] = distance(atom_1, atom_2)
    return lengths


def angle(atom_1, atom_2, atom_3):
    bond_1 = atom_1.position_vector - atom_2.position_vector
    bond_2 = atom_3.position_vector - atom_2.position_vector
    angle = math.acos(
        np.dot(bond_1, bond_2) / (
                np.linalg.norm(bond_1) * np.linalg.norm(bond_2))
        )
    angle = math.degrees(angle)
    return angle


def get_angles(
        entry: Residue,
        angle_query: list[tuple[int, int, int]]
        ) -> dict[tuple[int, int, int]: float]:
    angles = {}
    for name, trio in angle_query.items():
        atom_1 = entry[trio[0]]
        atom_2 = entry[trio[1]]
        atom_3 = entry[trio[2]]
        angles[name] = angle(atom_1, atom_2, atom_3)
    return angles


def dihedral(atom_1, atom_2, atom_3, atom_4):
    bond_1 = atom_2.position_vector - atom_1.position_vector
    bond_2 = atom_3.position_vector - atom_2.position_vector
    bond_3 = atom_4.position_vector - atom_3.position_vector
    dihedral = math.atan2(
        np.dot(
            np.linalg.norm(bond_2) * bond_1,
            np.cross(bond_2,
                     bond_3
                     )
            ),
        np.dot(
            np.cross(
                bond_1,
                bond_2
                ),
            np.cross(
                bond_2,
                bond_3
                )
            )
        )
    dihedral = math.degrees(dihedral)
    return dihedral


def get_dihedrals(
        entry: Residue,
        dihedral_query: list[tuple[int, int, int, int]]
        ) -> dict[tuple[int, int, int, int]: float]:
    dihedrals = {}
    for name, quartet in dihedral_query.items():
        atom_1 = entry[quartet[0]]
        atom_2 = entry[quartet[1]]
        atom_3 = entry[quartet[2]]
        atom_4 = entry[quartet[3]]
        dihedrals[name] = dihedral(atom_1, atom_2, atom_3, atom_4)
    return dihedrals

def csv_to_internal_coords():
    args = get_args()
    config_path = Path(args['query-file-path'])
    with open(config_path) as config_file:
        length_query, angle_query, dihedral_query = parse_query(config_file)
    input_path = Path(args['input-file-path'])
    output_path = Path(args['output-file-path'])
    with open(input_path, "r") as input_file, open(output_path,"w") as output_file:
        residue_data = read_residues(input_file)
        
        header = ["PDB ID", "Chain ID", "Residue Index", "AltLoc", "Insertion Code", "Subsequent Residue"]
        for bond in length_query.keys():
            header.append(bond)
        for angle in angle_query.keys():
            header.append(angle)
        for dihedral in dihedral_query.keys():
            header.append(dihedral)
            
        csvwriter = csv.DictWriter(
            output_file,
            fieldnames=header
            )
        csvwriter.writeheader()
        for entry in residue_data:
            lengths = get_lengths(entry, length_query)
            angles = get_angles(entry, angle_query)
            dihedrals = get_dihedrals(entry, dihedral_query)
            coordinates = {
                                  "PDB ID": entry.pdb_id,
                                  "Chain ID": entry.chain_id,
                                  "Residue Index": entry.residue_index,
                                  "AltLoc": entry.altloc,
                                  "Insertion Code": entry.insertion_code,
                                  "Subsequent Residue": entry.subsequent_residue
                                  } | lengths | angles | dihedrals
            csvwriter.writerow(coordinates)

if __name__ == "__main__":
    csv_to_internal_coords()