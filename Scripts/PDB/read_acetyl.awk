BEGIN { OFS = ","
	FIELDWIDTHS = "6 5 5 1 3 2 4 1 11 8 8 6 6 12 2"
}
	{if ($1 ~ /^ATOM/) {
		read_id = $7	
		gsub(/[[:space:]]/,"",read_id)
		if (read_id == prev_residue) { 
			read_chain = $6
                	gsub(/[[:space:]]/,"",read_chain)
			if (read_chain == chain) {
				read_code = $8
                		gsub(/[[:space:]]/,"",read_code)
				if (in_code == read_code) {
					if  ($3 ~ /^[[:space:]]*(C|CA|O)[[:space:]]*$/)
						print protein, read_chain, residue, read_code, $4, $5, $3, $9, $10, $11
				}
			}
		}
	}
} 
