package main

import (
	"fmt"
)

func Sqrt(x float64) (float64, int) {
	z := float64(x/2)
	i := int(0)
	for  ; i < 10 ; i++ {
		fmt.Println(z)
		theta := (z*z - x) / (2*z)
		if theta == 0 {
			break
		}
		z = z-theta
		
	}
	return z, i
}

func main() {
	theSqrt, iteration := Sqrt(1024)
	fmt.Println(theSqrt, iteration)
}
