

### Branch Prediction (Correlated with Spectre Bugs) 

Branch prediction is a CPU optimization technique that predicts the direction of branch instructions to improve the flow of instruction execution. While this technique can significantly enhance performance, it also introduces potential security vulnerabilities.

Spectre bugs exploit the speculative execution feature of modern processors, which relies on branch prediction. By manipulating the prediction, an attacker can cause the CPU to speculatively execute instructions that access sensitive data. Although these speculative executions are not completed and their results are discarded, the changes they make to the cache can be measured to infer the accessed data, leading to potential data leaks.
For more information on how branch prediction impacts performance, you can refer to this [Stack Overflow discussion on why processing a sorted array is faster than processing an unsorted array](https://stackoverflow.com/questions/11227809/why-is-processing-a-sorted-array-faster-than-processing-an-unsorted-array) .
