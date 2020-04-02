package main

import (
	"fmt"
	"io"
	"os"

	bst "github.com/me/Compression-and-Methods-of-Coding/binary_search_tree"
	bits "github.com/me/Compression-and-Methods-of-Coding/bits"
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
	file.Close()

	compressedAlphabet := staticHuffman(repetitions, counter)
	bitString := ""
	bytesRes := make([]byte, 0)
	fmt.Println(compressedAlphabet)
	file, err = os.Open(os.Args[1])
	check(err)

	for {
		_, err = file.Read(curr)
		if err != nil && err == io.EOF {
			break
		}
		bitString += compressedAlphabet[curr[0]]
		if len(bitString)%8 == 0 {
			bytesRes = append(bytesRes, bits.Bits2bytes(bitString)...)
			bitString = ""
		}
	}
	if len(bitString) != 0 {
		for ok := true; ok; ok = (len(bitString) != 8) {
			bitString = "0" + bitString
		}
		bytesRes = append(bytesRes, bits.Bits2bytes(bitString)...)
	}

	fmt.Println(bytesRes)
}

func staticHuffman(reps map[byte]float64, counter float64) map[byte]string {
	ns := make(bst.Nodes, 0, len(reps))
	for k, v := range reps {
		ns = append(ns, bst.MakeNode(v/counter, int16(k)))
	}

	var newRoot, n1, n2 *bst.Node
	for fin := false; !fin; fin = (len(ns) == 1) {
		ns, n1, n2 = ns.Pop2Min()
		newRoot = bst.MakeNode(n1.Value+n2.Value, -1)
		newRoot.Left = n1
		newRoot.Right = n2
		ns = append(ns, newRoot)

	}

	var makeBitsMap func(parent *bst.Node, codeWords map[byte]string)
	codeWords := make(map[byte]string)

	makeBitsMap = func(parent *bst.Node, codeWords map[byte]string) {
		if parent.Symbol == -1 {
			parent.Left.Codeword = parent.Codeword + "0"
			parent.Right.Codeword = parent.Codeword + "1"
			makeBitsMap(parent.Left, codeWords)
			makeBitsMap(parent.Right, codeWords)
		} else if parent.Symbol != -2 {
			codeWords[byte(parent.Symbol)] = parent.Codeword
		}
	}

	makeBitsMap(ns[0], codeWords)

	return codeWords
}
