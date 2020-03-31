package main

import (
	"fmt"
	"io"
	"os"

	bst "github.com/me/Compression-and-Methods-of-Coding/binary_search_tree"
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
	probability := make(bst.Nodes, 0, len(reps))
	for k, v := range reps {
		probability = append(probability, bst.MakeNode(float64(v/counter), k))
	}

	//n1, n2 := probability[0], probability[1]

}
