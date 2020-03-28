**Task description:**<br>
For discreet random variables X and Y entropy of Y conditioned upon X can be described with equation:<br><br>
![\Large H(Y|X) = \sum_{x\in X} P(x) * H(Y|x)](https://latex.codecogs.com/svg.latex?H(Y|X)%3D\sum_{x\in%20X}%20P(x)%20*%20H(Y|x))<br>
where:<br><br>
![\Large H(Y|x) = \sum_{y\in Y} P(y|x) * I(y|x)](https://latex.codecogs.com/svg.latex?H(Y|x)%3D\sum_{y\in%20Y}%20P(y|x)%20*%20I(y|x))<br>
and:<br>
  P(x) - probability of x <br>
  I(x) - information correlated with x <br>
  y|x - event 'y' occurring given that event 'x' has (by assumption, presumption, assertion or evidence) occurred. <br><br>
Create a program that, for given file (treated as stream of 8-bit symbols) will count the frequency of each symbol nad frequency of symbol with given prefix (symbol before is given, for fist sign it will be symbol coded as 0).<br><br>
Create function that will calculate entropy and conditional entropy for counted frequencies, and return difference between those two numbers. 

**Usage**<br>
This program was tested under Linux (more specifically Archlinux 5.5.10). To lauch it you gonna need Golang compiler.<br>
\> *go run ex1.go <filename>*
