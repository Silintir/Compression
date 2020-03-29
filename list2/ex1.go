package main

import (
	"fmt"
	"io"
	"os"
)

func check(e error) {
	if e != nil {
		panic(e)
	}
}

func main() {
	if len(os.Args) < 3 {
		fmt.Printf("Missing some arguments, correct form is: %s <input_file> <output_file>", os.Args[0])
	}
	file, err := os.Open(os.Args[1])
	check(err)

	repetitions := make(map[byte]int)
	curr := make([]byte, 1)
	counter := 0

	for {
		_, err = file.Read(curr)
		check(err)
		if err == io.EOF {
			break
		}
		repetitions[curr[0]]++
		counter++
	}

}

func classicHuffman(reps map[byte]int, counter int) {
	probability := make(map[byte]float64)
	for k, v := range reps {
		probability[k] = float64(v / counter)

	}
}
