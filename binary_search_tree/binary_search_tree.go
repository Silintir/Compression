package binarysearchtree

import (
	"fmt"
)

// Node : Basic node to build BST
type Node struct {
	Value    float64
	Symbol   int16
	Codeword string
	Left     *Node
	Right    *Node
	Parent   *Node
}

var nullNode Node = Node{Value: -1, Symbol: -2, Codeword: "", Left: nil, Right: nil, Parent: nil}

// MakeNode : wrapper to make creating nodes more convinient
func MakeNode(v float64, symbol int16) *Node {
	return &Node{Value: v, Symbol: symbol, Codeword: "", Left: &nullNode, Right: &nullNode, Parent: &nullNode}
}

// Insert : node to preexisting tree/root node
func (root *Node) Insert(node *Node) {
	curr := &root
	var parent *Node = nil
	for ok := true; ok; ok = (*curr != &nullNode) {
		parent = *curr
		if node.Value < parent.Value {
			curr = &parent.Left
		} else {
			curr = &parent.Right
		}
	}
	node.Parent = parent
	*curr = node
}

// Print : list whole tree
func (root *Node) Print() {
	showInOrder(root)
}

func showInOrder(root *Node) {
	if root.Symbol != -2 {
		showInOrder(root.Left)
		fmt.Println(root.Value, " ", root.Symbol)
		showInOrder(root.Right)
	}
}

// Nodes : type for array of Nodes, to wrap the type for some array specific functions
type Nodes []*Node

// FindIndexMin - finds the index of node with the smallest peobablity
func (ns Nodes) FindIndexMin() int {
	min := 0
	for i, node := range ns {
		if node.Value < ns[min].Value {
			min = i
		}
	}
	return min
}

// PopMin - pop smallest element from slice elegant way
func (ns Nodes) PopMin() (Nodes, *Node) {
	minIndex := ns.FindIndexMin()
	min := ns[minIndex]
	ns[minIndex] = ns[len(ns)-1]
	return ns[:len(ns)-1], min
}

// Pop2Min - pop 2 smallest elements from slice elegant way
func (ns Nodes) Pop2Min() (Nodes, *Node, *Node) {
	var min1, min2 *Node
	ns, min1 = ns.PopMin()
	ns, min2 = ns.PopMin()

	return ns, min1, min2
}
