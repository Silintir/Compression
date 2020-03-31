package binarysearchtree

import (
	"fmt"
)

// Node : Basic node to build BST
type Node struct {
	Value  float64
	Symbol byte
	Left   *Node
	Right  *Node
	Parent *Node
}

// Nodes : type for array of Nodes, to wrap the type for some array specific functions
type Nodes []*Node

// FindMin - finds the node with the smallest peobablity
func (n Nodes) FindMin() *Node {
	min := n[0]
	for _, node := range n {
		if node.Value < min.Value {
			min = node
		}
	}
	return min
}

// Remove element from slice elegant way
func (n Nodes) Remove(s []int, i int) []int {
	s[i] = s[len(s)-1]
	return s[:len(s)-1]
}

var nullNode Node = Node{Value: -1, Symbol: 0, Left: nil, Right: nil, Parent: nil}

// MakeNode : wrapper to make creating nodes more convinient
func MakeNode(v float64, symbol byte) *Node {
	return &Node{Value: v, Symbol: symbol, Left: &nullNode, Right: &nullNode, Parent: &nullNode}
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
	if root != &nullNode {
		showInOrder(root.Left)
		fmt.Println(root.Value)
		showInOrder(root.Right)
	}
}
