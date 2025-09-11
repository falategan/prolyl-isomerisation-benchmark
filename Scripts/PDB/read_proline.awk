BEGIN { OFS = ","
	FIELDWIDTHS = "6 5 5 1 3 2 4 1 11 8 8 6 6 12 2"
}
	{ if ($1 == "ATOM  " && $5=="PRO") 
		print protein, $6, $7, $8, $4, $3, $9, $10, $11
} 
