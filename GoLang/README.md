# Notes from Learning GO 
> [nice to read](https://gobyexample.com/)
## declare varialbes

for declare variables use := or var = 
i := 4 
i int := 4

var i = 4
var i int = 4

## define constant

const j = 444
const j int = 3

ERR: const j := 3
ERR: const j int := 3

## declare function

func test1(input1 <input_type>) <return_type> { return [something]}

func test2(input1 , input2 <input_type>) <return_type> { return [something]}

func test3(input1 <input_type>, input2 <input_type>) <return_type> { return [something]}

## loops

### for loop

for i := 0; i < 10; i++ {	}

for ; sum < 1000; { }

no paranteces needed !...

for sum < 1000

like while in C

for {} // infinite loop

## if

if x < 0 {}

parentheses **not** needed

but braces **do needed**

if v := math.Pow(x, n); v < lim {
    return v
} else {
    // v is accessaible
}

`v` is only accessible inside **if** and **else** block

[continue here](https://go.dev/tour/flowcontrol/9)