package main 

import (
	"fmt"
	"os"
	"io"
	"math"
)

type Pair struct {
	Prev byte
	Curr byte
}

func check(e error)  {
	if e != nil {
		panic(e)
	}
}

func main()  {
	
	if len(os.Args) < 2 {
		fmt.Println("Brakujacy plik wejsciowy")
	}

	file, err := os.Open(os.Args[1])
	check(err)

	defer file.Close()
	
	prev := make([]byte,1)
	prev[0] = byte(0)
	curr := make([]byte,1)

	repetitions := make(map[byte]int)
	reps_with_prefix := make(map[Pair]int)
	counter := 0

	for  {
		_, err = file.Read(curr)
        if err != nil && err == io.EOF {
    	    break
		}
		check(err)

		repetitions[curr[0]] += 1
		reps_with_prefix[Pair{prev[0], curr[0]}] += 1
		
		prev[0] = curr[0]
		counter++
	}
	fmt.Println("Entropia :")
	e := entropy(repetitions, counter)
	fmt.Println(e)
	fmt.Println("Entropia warunkowa :")
	ew := entropyW(reps_with_prefix, repetitions, counter)
	fmt.Println(ew)
	fmt.Println("Roznica :")
	fmt.Println(e-ew)
}

func entropy(reps map[byte]int, counter int) float64 {
	var P, I, sum float64
	for _, value := range reps {
		P = float64(value)/float64(counter)
		I = -math.Log2(P)
		sum += P*I
	}
	return sum
}

func entropyW(repsW map[Pair]int, reps map[byte]int, counter int) float64 {
	var  W, P, sum float64
	//reps[0] += 1
	partial_sums := make(map[byte]float64)
	for pair, value := range repsW {
		W = float64(value)/float64(reps[pair.Prev])
		partial_sums[pair.Prev] -= math.Log2(W)*W
	}
	for key, value := range reps {
		P = float64(value)/float64(counter)
		sum += P*partial_sums[key]
	}
	return sum
}
