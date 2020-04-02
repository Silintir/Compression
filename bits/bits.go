package bits

// Bits2bytes converts increments of 8 bits (in string format) to bytes
func Bits2bytes(bits string) []byte {

	result := make([]byte, 0, (len(bits) / 8))
	for i := 0; i < (len(bits) / 8); i++ {
		result = append(result, bits2byte(bits[i*8:(i+1)*8]))
	}

	return result
}

func bits2byte(b string) byte {
	multiplier, result := 1, 0

	for i := 7; i >= 0; i-- {
		if b[i] == '1' {
			result += multiplier
		}
		multiplier *= 2
	}
	return byte(result)
}
