# Neural Networks Basics

**Summary**: Feedforward neural networks are the foundation of deep learning, consisting of input, hidden, and output layers that process data through weighted connections and activation functions.

**Sources**: [[A Mesterséges Neurális Hálózat alapjai – 1. rész]], [[Mesterséges Neurális Hálózat alapjai – 2. rész]]

**Last updated**: 2026-04-20

---

## Network Architecture

A feedforward neural network consists of three layer types:

- **Input Layer**: Receives observed data. Each neuron represents one feature/dimension.
- **Hidden Layer**: Performs computations. Models relationships between input features.
- **Output Layer**: Produces the final prediction.

Layers are fully connected: every neuron in one layer connects to every neuron in the next layer.

## Forward Propagation

Forward propagation is the process of computing predictions. Data flows from input to output.

### Neuron Computation

Each neuron computes a weighted sum of its inputs, then applies an activation function:

$$z_j = w_{0j} + \sum_{i=1}^n x_i w_{ij}$$

Where:
- $w_{0j}$ is the bias (always receives input of 1)
- $w_{ij}$ are weights connecting input $i$ to neuron $j$
- $x_i$ are input values

The result passes through an activation function $f(z)$ to produce the output.

### Common Activation Functions

- **Tanh**: $f(z) = 1 - \frac{2}{e^{2z} + 1}$
- **ReLU**: $f(u) = \max(0, u)$

### Example Calculation

Given:
$$x = \begin{bmatrix} 0.05 \\ 0.1 \end{bmatrix}$$

Hidden layer weights (excluding bias):
$$w = \begin{bmatrix} 0.15 & 0.25 & 0.35 \\ 0.45 & 0.55 & 0.65 \end{bmatrix}$$

Calculating $z$ values and applying Tanh produces:
$$o_r = \begin{bmatrix} 0.195 \\ 0.495 \\ 0.710 \end{bmatrix}$$

Then applying ReLU to the output layer produces the final prediction:
$$o = \begin{bmatrix} 0.812 \\ 1.772 \end{bmatrix}$$

## Loss Calculation

After forward propagation, we compare the prediction to the actual result. The simplest loss function is quadratic error:

$$E = \frac{(y - o)^2}{2}$$

Where $y$ is the true value and $o$ is the predicted value.

## Backpropagation

Backpropagation updates weights to reduce error. It flows backward from output to input, computing gradients using the chain rule.

### Chain Rule Application

To update weights, we compute partial derivatives:

$$\frac{\partial E}{\partial w_{11}} = \frac{\partial E}{\partial o_1} \cdot \frac{\partial f_k(u_1)}{\partial u_1} \cdot \frac{\partial u_1}{\partial v_{11}}$$

### Gradient Descent Update

Weights are updated as:
$$w_{new} = w_{old} - \eta \cdot \frac{\partial E}{\partial w}$$

Where $\eta$ is the learning rate.

### Important Notes

1. **Hidden layer gradients**: Must aggregate errors from all output neurons that receive input from that hidden neuron.

2. **Local minimum**: Only guaranteed to find a local minimum, not necessarily the global optimum.

3. **Data quality**: A neural network is only as good as the data it's trained on.

## Related pages

- [[seq2seq]]
- [[recurrent-neural-networks]]
- [[activation-functions]]