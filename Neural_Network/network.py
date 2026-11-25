"""A small fully connected neural network written with NumPy only.

The network is a value function: it looks at a board *after* a move has been
made (an "afterstate") and predicts how good that position is for the player
who just moved, as a number between -1 (loss) and +1 (win). 0 means a draw.

Boards are handled here as flat NumPy arrays of length rows * columns, with
1 for X, -1 for O and 0 for an empty square.
"""

from __future__ import annotations

from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

X_VALUE = 1
O_VALUE = -1
EMPTY_VALUE = 0


# --------------------------------------------------------------------------- #
# Board encoding
# --------------------------------------------------------------------------- #
def encode_boards(boards: np.ndarray, player: int) -> np.ndarray:
    """Turn boards into network input, seen from ``player``'s point of view.

    ``boards`` has shape (batch, cells). The result has shape (batch, 2 * cells):
    the first half marks ``player``'s pieces, the second half the opponent's.
    Encoding from the mover's point of view lets one network play both X and O.
    """
    boards = np.atleast_2d(boards)
    mine = (boards == player).astype(np.float32)
    theirs = (boards == -player).astype(np.float32)
    return np.concatenate([mine, theirs], axis=1)


def candidate_afterstates(
    board: np.ndarray,
    legal_cells: Sequence[int],
    player: int,
) -> np.ndarray:
    """Encode every board reachable by ``player`` making one legal move."""
    legal_cells = np.asarray(legal_cells, dtype=np.int64)
    candidates = np.repeat(board[None, :], len(legal_cells), axis=0)
    candidates[np.arange(len(legal_cells)), legal_cells] = player
    return encode_boards(candidates, player)


def symmetry_permutations(rows: int, columns: int) -> List[np.ndarray]:
    """Index permutations for every rotation/reflection that keeps the board shape.

    A square board has 8 symmetries; a rectangular board has 4. They are used to
    multiply the training data, because a position and its mirror image are
    equally good.
    """
    grid = np.arange(rows * columns).reshape(rows, columns)
    variants = [grid, grid[::-1, :], grid[:, ::-1], grid[::-1, ::-1]]
    if rows == columns:
        transposed = grid.T
        variants += [
            transposed,
            transposed[::-1, :],
            transposed[:, ::-1],
            transposed[::-1, ::-1],
        ]
    return [variant.reshape(-1).copy() for variant in variants]


def augment_with_symmetries(
    inputs: np.ndarray,
    permutations: Sequence[np.ndarray],
) -> np.ndarray:
    """Return ``inputs`` under every symmetry, stacked along the batch axis."""
    cells = inputs.shape[1] // 2
    planes = inputs.reshape(inputs.shape[0], 2, cells)
    return np.concatenate(
        [planes[:, :, permutation].reshape(inputs.shape[0], 2 * cells)
         for permutation in permutations],
        axis=0,
    )


# --------------------------------------------------------------------------- #
# Multilayer perceptron
# --------------------------------------------------------------------------- #
class MLP:
    """Multilayer perceptron: ReLU hidden layers and a single tanh output.

    Trained with mean squared error and the Adam optimizer.
    """

    def __init__(self, layer_sizes: Sequence[int], seed: Optional[int] = None) -> None:
        if len(layer_sizes) < 2 or layer_sizes[-1] != 1:
            raise ValueError("layer_sizes must start with the input size and end with 1")

        rng = np.random.default_rng(seed)
        self.layer_sizes = [int(size) for size in layer_sizes]
        self.weights: List[np.ndarray] = []
        self.biases: List[np.ndarray] = []
        for n_in, n_out in zip(self.layer_sizes[:-1], self.layer_sizes[1:]):
            # He initialisation suits ReLU layers.
            self.weights.append(
                rng.normal(0.0, np.sqrt(2.0 / n_in), (n_in, n_out)).astype(np.float32)
            )
            self.biases.append(np.zeros(n_out, dtype=np.float32))

        self._adam_step = 0
        self._m = [np.zeros_like(p) for p in self._parameters()]
        self._v = [np.zeros_like(p) for p in self._parameters()]

    @property
    def input_size(self) -> int:
        return self.layer_sizes[0]

    def _parameters(self) -> List[np.ndarray]:
        return [*self.weights, *self.biases]

    def forward(self, inputs: np.ndarray) -> np.ndarray:
        """Predict values for a batch of encoded boards. Returns shape (batch,)."""
        activation = np.atleast_2d(inputs).astype(np.float32, copy=False)
        last = len(self.weights) - 1
        for index, (weight, bias) in enumerate(zip(self.weights, self.biases)):
            activation = activation @ weight + bias
            activation = np.tanh(activation) if index == last else np.maximum(activation, 0.0)
        return activation[:, 0]

    def train_step(
        self,
        inputs: np.ndarray,
        targets: np.ndarray,
        learning_rate: float = 1e-3,
        beta1: float = 0.9,
        beta2: float = 0.999,
        epsilon: float = 1e-8,
    ) -> float:
        """Do one gradient step on a mini-batch and return its loss."""
        inputs = np.atleast_2d(inputs).astype(np.float32, copy=False)
        targets = np.asarray(targets, dtype=np.float32).reshape(-1)
        batch_size = inputs.shape[0]

        # Forward pass, keeping every layer's output for backpropagation.
        activations = [inputs]
        last = len(self.weights) - 1
        for index, (weight, bias) in enumerate(zip(self.weights, self.biases)):
            z = activations[-1] @ weight + bias
            activations.append(np.tanh(z) if index == last else np.maximum(z, 0.0))

        output = activations[-1][:, 0]
        error = output - targets
        loss = float(np.mean(error ** 2))

        # Backward pass.
        grad_z = (2.0 / batch_size) * error[:, None] * (1.0 - activations[-1] ** 2)
        weight_grads: List[np.ndarray] = [np.empty(0)] * len(self.weights)
        bias_grads: List[np.ndarray] = [np.empty(0)] * len(self.biases)
        for index in range(last, -1, -1):
            weight_grads[index] = activations[index].T @ grad_z
            bias_grads[index] = grad_z.sum(axis=0)
            if index > 0:
                grad_a = grad_z @ self.weights[index].T
                grad_z = grad_a * (activations[index] > 0.0)

        # Adam update.
        self._adam_step += 1
        correction1 = 1.0 - beta1 ** self._adam_step
        correction2 = 1.0 - beta2 ** self._adam_step
        for parameter, gradient, m, v in zip(
            self._parameters(), [*weight_grads, *bias_grads], self._m, self._v
        ):
            m *= beta1
            m += (1.0 - beta1) * gradient
            v *= beta2
            v += (1.0 - beta2) * gradient ** 2
            parameter -= (
                learning_rate * (m / correction1) / (np.sqrt(v / correction2) + epsilon)
            ).astype(np.float32)

        return loss

    def save(self, path: str, **metadata: object) -> None:
        """Save weights (and extra metadata such as the board size) to a .npz file."""
        arrays: Dict[str, object] = {
            "layer_sizes": np.array(self.layer_sizes, dtype=np.int64)
        }
        for index, (weight, bias) in enumerate(zip(self.weights, self.biases)):
            arrays[f"W{index}"] = weight
            arrays[f"b{index}"] = bias
        for key, value in metadata.items():
            arrays[f"meta_{key}"] = np.array(value)
        np.savez(path, **arrays)

    @classmethod
    def load(cls, path: str) -> Tuple["MLP", Dict[str, object]]:
        """Load a network saved with :meth:`save`. Returns (network, metadata)."""
        with np.load(path) as data:
            network = cls(data["layer_sizes"].tolist())
            for index in range(len(network.weights)):
                network.weights[index] = data[f"W{index}"].astype(np.float32)
                network.biases[index] = data[f"b{index}"].astype(np.float32)
            metadata = {
                key[len("meta_"):]: data[key].item()
                for key in data.files
                if key.startswith("meta_")
            }
        return network, metadata
