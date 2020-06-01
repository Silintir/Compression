package main

import (
	"fmt"
	"io/ioutil"
	"os"
)

type pixel struct {
	Red   byte
	Green byte
	Blue  byte
}

func check(e error) {
	if e != nil {
		panic(e)
	}
}

func main() {

	if len(os.Args) < 2 {
		fmt.Println("Brakujacy plik wejsciowy")
	}

	f, err := ioutil.ReadFile(os.Args[1])
	check(err)

	width := int(f[12])
	height := int(f[14])

	imgDescr := f[17]

	order := (imgDescr & 48) >> 4

	bitmap := make([]pixel, int(width*height))

	off := 18

	if (order & 0x10) != 0 {
		if (order & 0x01) == 0 {
			for i := 0; i < height; i++ {
				for j := 0; j < width; j++ {
					bitmap[i*width+j] = pixel{f[off], f[off+1], f[off+2]}
					off += 3
				}
			}
		} else {
			for i := 0; i < height; i++ {
				for j := width; j > 0; j-- {
					bitmap[i*width+j] = pixel{f[off], f[off+1], f[off+2]}
					off += 3
				}
			}
		}
	} else {
		if (order & 0x01) == 0 {
			for i := height; i > 0; i-- {
				for j := 0; j < width; j++ {
					bitmap[i*width+j] = pixel{f[off], f[off+1], f[off+2]}
					off += 3
				}
			}
		} else {
			for i := height; i > 0; i-- {
				for j := width; j > 0; j-- {
					bitmap[i*width+j] = pixel{f[off], f[off+1], f[off+2]}
					off += 3
				}
			}
		}
	}

	fmt.Println(bitmap[23])
	fmt.Println(bitmap[47])
}
