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

	fmt.Print(staticHuffman(repetitions, counter))

}

func staticHuffman(reps map[byte]float64, counter float64) map[byte]string {
	ns := make(bst.Nodes, 0, len(reps))
	fmt.Println(reps)
	for k, v := range reps {
		ns = append(ns, bst.MakeNode(v/counter, int16(k)))
	}
	//debug
	for i := 0; i < len(ns); i++ {
		fmt.Println(ns[i].Value)
	}

	var newRoot, n1, n2 *bst.Node
	for fin := false; !fin; fin = (len(ns) == 1) {
		// TODO: POP2MIN not working correctly
		ns, n1, n2 = ns.Pop2Min()
		fmt.Println(n1.Value, " ", n2.Value)
		newRoot = bst.MakeNode(n1.Value+n2.Value, -1)
		newRoot.Insert(n1)
		newRoot.Insert(n2)
		ns = append(ns, newRoot)

	}
	ns[0].Print()

	var codewordsCreate func(parent *bst.Node)
	codeWords := make(map[byte]string)

	codewordsCreate = func(parent *bst.Node) {
		if parent.Symbol == -1 {
			parent.Left.Codeword = parent.Codeword + "0"
			parent.Right.Codeword = parent.Codeword + "1"
			fmt.Println("Aaaa")
			codewordsCreate(parent.Left)
			codewordsCreate(parent.Right)
		} else {
			codeWords[byte(parent.Symbol)] = parent.Codeword
		}
	}

	codewordsCreate(ns[0])

	return codeWords
}
