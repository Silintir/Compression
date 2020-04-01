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

	repetitions := make(map[byte]float64)
	curr := make([]byte, 1)
	counter := 0.0

	for {
		_, err = file.Read(curr)
		if err != nil && err == io.EOF {
			break
		}
		repetitions[curr[0]]++
		counter++
	}

	classicHuffman(repetitions, counter).Print()

}

func classicHuffman(reps map[byte]float64, counter float64) *bst.Node {
	ns := make(bst.Nodes, 0, len(reps))
	for k, v := range reps {
		ns = append(ns, bst.MakeNode(v/counter, int16(k)))
	}
	var newRoot, n1, n2 *bst.Node
	for fin := false; !fin; fin = (len(ns) == 1) {
		ns, n1, n2 = ns.Pop2Min()
		newRoot = bst.MakeNode(n1.Value+n2.Value, -1)
		newRoot.Insert(n1)
		newRoot.Insert(n2)
		ns = append(ns, newRoot)

	}

	return ns[0]
}
