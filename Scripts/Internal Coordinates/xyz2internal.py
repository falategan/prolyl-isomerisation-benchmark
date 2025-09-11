import argparse
from pathlib import Path
from typing import IO
import numpy as np
import math
import csv


class XyzEntry:
    def __init__(
            self,
            index: int,
            header: str
            ):
        self.header = header
        self.index = index
        self.atoms = {}
    
    def add_coordinate(
            self,
            index: int,
            line: str
            ):
        line = line.split()
        self.atoms[index] = Atom(
            self,
            index,
            line[0],
            float(line[1]),
            float(line[2]),
            float(line[3])
            )
    
    def __str__(self) -> str:
        string = f"Entry {self.index}\n{self.header}\n"
        for index, atom in self.atoms.items():
            string += f"{index}\t{atom.atom_type}\t{atom.position_vector}\n"
        return string
    
    def __getitem__(self, key):
        return self.atoms[key]


class Atom:
    def __init__(
            self,
            entry: XyzEntry,
            index: int,
            atom_type: str,
            x: float,
            y: float,
            z: float
            ):
        self.entry = entry
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
        prog="xyz_to_internal_coords",
        description="reads xyz or allxyz file and returns the internal "
                    "coordinates of each model in csv format"
        )
    parser.add_argument("input-file-path")
    parser.add_argument("query-file-path")
    parser.add_argument("output-file-path")
    return vars(parser.parse_args())


def read_xyz(file: IO):
    header_count = 0
    new_entry = None
    coordinate_index = 0
    entry_index = 1
    for line in file:
        if header_count < 2:
            if header_count == 1:
                new_entry = XyzEntry(entry_index, line)
            header_count += 1
            continue
        if line != ">\n":
            new_entry.add_coordinate(
                coordinate_index,
                line
                )
            coordinate_index += 1
            continue
        header_count = 0
        coordinate_index = 0
        entry_index += 1
        yield new_entry
    yield new_entry


def parse_query(file):
    lengths = {}
    angles = {}
    dihedrals = {}
    for line in file:
        columns = line.split()
        if columns[1] == "B":
            lengths[columns[0]] = (
                    (int(columns[2]),
                     int(columns[3])
                     )
            )
        elif columns[1] == "A":
            angles[columns[0]] = (
                    (int(columns[2]),
                     int(columns[3]),
                     int(columns[4])
                     )
            )
        elif columns[1] == "D":
            dihedrals[columns[0]] = (
                    (int(columns[2]),
                     int(columns[3]),
                     int(columns[4]),
                     int(columns[5])
                     )
            )
        else:
            raise ValueError(
                f"Unrecognised internal coordinate type '{columns[1]}' "
                f"in the line:\n"
                f" {line}.\n"
                f"Only the following coordinate types are supported:\n"
                f" 'B': Bond lengths\n"
                f" 'A': Bond angles\n"
                f" 'D': Dihedral angles\n"
                )
    return lengths, angles, dihedrals


def distance(atom_1, atom_2):
    distance = np.linalg.norm(
        atom_2.position_vector - atom_1.position_vector
        )
    return distance


def get_lengths(
        entry: XyzEntry,
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
        entry: XyzEntry,
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
        entry: XyzEntry,
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


def xyz_to_internal_coords():
    args = get_args()
    config_path = Path(args['query-file-path'])
    with open(config_path) as config_file:
        length_query, angle_query, dihedral_query = parse_query(config_file)
    
    input_path = Path(args['input-file-path'])
    output_path = Path(args['output-file-path'])
    with open(input_path, "r") as input_file, open(output_path,
                                                   "w"
                                                   ) as output_file:
        xyz_data = read_xyz(input_file)
        header = ["Index"]
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
        for entry in xyz_data:
            lengths = get_lengths(entry, length_query)
            angles = get_angles(entry, angle_query)
            dihedrals = get_dihedrals(entry, dihedral_query)
            coordinates = lengths | angles | dihedrals
            coordinates["Index"] = entry.index
            csvwriter.writerow(coordinates)


if __name__ == "__main__":
    xyz_to_internal_coords()


