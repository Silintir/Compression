package main

import (
	"fmt"
	"io"
	"io/ioutil"
	"math"
	"os"
	"time"
)

const maxUint32 = uint64(^uint32(0))
const minUint32 = uint64(0)

// Probability somethin
type probability struct {
	low         uint64
	high        uint64
	denominator uint64
}

type bitarray struct {
	array      []byte
	offset     int // 0-7 bits, -1 for going to next byte
	byteOffset int
}

func check(e error) {
	if e != nil {
		panic(e)
	}
}

func getBit(b byte) {

}

func (array *bitarray) pushBit(bit bool) {
	if array.offset == -1 {
		array.array = append(array.array, 0)
		array.offset = 7

	}
	if bit {
		array.array[len(array.array)-1] += byte(math.Pow(2, float64(array.offset)))
	}
	array.offset--
}

func (array *bitarray) readBit() bool {
	bit := false
	if (array.array[array.byteOffset] & byte(math.Pow(2, float64(array.offset)))) != 0 {
		bit = true
	}
	array.offset--
	if array.offset == -1 {
		array.byteOffset++
		if array.byteOffset >= len(array.array) {
			fmt.Print("file ended ungracefully")
		}
	}
	return bit
}

// MakeModel - set your prp array to def
func makeModel() []uint64 {
	arr := make([]uint64, 258)
	for i := range arr {
		arr[i] = uint64(i)
	}
	return arr
}

func getProbability(probArray []uint64, char uint64) *probability {
	r := probability{probArray[char], probArray[char+1], probArray[257]}
	if probArray[257] < ((maxUint32 / 4) + 1) {
		for i := char + 1; i < 258; i++ {
			probArray[i]++
		}
	}
	return &r
}
func getChar(probArray []uint64, val uint64) uint64 {
	for i := 0; i < len(probArray)-1; i++ {
		if val < probArray[i+1] {
			return uint64(i)
		}
	}
	return 256
}

func compress(inFile string, outFile string) {
	probArray := makeModel()
	high, low, count := uint64(65535), uint64(0), 0
	output := bitarray{[]byte{0}, 7, 0}

	encodeChar := func(char uint64) {
		prob := getProbability(probArray, char)
		d := high - low + 1
		high = low + (d*prob.high)/prob.denominator - 1
		low += (d * prob.low) / prob.denominator

		for {
			if high < 32768 {
				low <<= 1
				high = (high << 1) + 1
				output.pushBit(false)
				for i := 0; i < count; i++ {
					output.pushBit(true)
				}
				count = 0
			} else if low >= 32768 {
				low = (low - 32768) << 1
				high = ((high - 32768) << 1) + 1
				output.pushBit(true)
				for i := 0; i < count; i++ {
					output.pushBit(false)
				}
				count = 0
			} else if (low >= 16384) && (high < 49152) {
				low = (low - 16384) << 1
				high = ((high - 16384) << 1) + 1
				count++
			} else {
				break
			}
		}
	}

	file, err := os.Open(inFile)
	check(err)
	defer file.Close()

	curr := make([]byte, 1)

	for {
		_, err = file.Read(curr)
		if err != nil && err == io.EOF {
			break
		}
		check(err)
		encodeChar(uint64(curr[0]))
	}

	encodeChar(256)
	count++

	if low <= 16384 {
		output.pushBit(false)
		for i := 0; i < count; i++ {
			output.pushBit(true)
		}
	} else {
		output.pushBit(true)
		for i := 0; i < count; i++ {
			output.pushBit(false)
		}
	}

	// return []byte to file
	fmt.Println(output.array)

	err = ioutil.WriteFile(outFile, output.array, 0644)
	if err != nil {
		panic(err)
	}
}

func decompress(inFile string, outFile string) {
	probArray := makeModel()
	high, low, res := uint64(65535), uint64(0), 0
	output := make([]byte, 0)

	b, err := ioutil.ReadFile(inFile)
	//fmt.Println(b)
	check(err)
	bits := bitarray{b, 7, 0}

	for i := 0; i < 16; i++ {
		res <<= 1
		if bits.readBit() {
			res++
		}
	}

	for {
		d := high - low + 1
		scval := ((uint64(res)-low+1)*probArray[257] - 1) / d
		fmt.Println(res, scval)
		time.Sleep(1 * time.Second)
		char := getChar(probArray, scval)
		if char == 256 {
			break
		} else {
			output = append(output, byte(char))
		}

		p := getProbability(probArray, char)

		high = low + (p.high*d)/p.denominator - 1
		low += (d * p.low) / p.denominator

		for {
			if high < 32768 {
				low <<= 1
				high = (high << 1) + 1
				res <<= 1
				if bits.readBit() {
					res++
				}
			} else if low >= 32768 {
				low = (low - 32768) << 1
				high = ((high - 32768) << 1) + 1
				res = ((res - 32768) << 1)
				if bits.readBit() {
					res++
				}
			} else if (low >= 16384) && (high < 49152) {
				low = (low - 16384) << 1
				high = ((high - 16384) << 1) + 1
				res = ((res - 16384) << 1)
				if bits.readBit() {
					res++
				}
			} else {
				break
			}
		}
	}
	fmt.Print(output)
	err = ioutil.WriteFile(outFile, output, 0644)
	if err != nil {
		panic(err)
	}

}

func main() {
	//compress("testfile", "res")
	decompress("res", "res1")
}
