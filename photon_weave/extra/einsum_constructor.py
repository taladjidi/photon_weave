import itertools
from typing import TYPE_CHECKING, Dict, List, Union

if TYPE_CHECKING:
    from photon_weave.state.base_state import BaseState


def apply_operator_vector(state_objs: list, operator_objs: list) -> str:
    """
    Constructs an Einstein Sum string
    for multiplying an operator with a state vector, where
    operator can be applied to the subspace.

    Parameters
    ----------
    state_objs: List[BaseState]
        List of all State objects which are in the product space
        The order should reflect the order in the tensoring
    operator_objs: List[BaseState]
        List of State objects on which the operator should be applied

    Returns
    -------
    str
        Einstein string that achieves the application

    Notes
    -----
    - The arrays should not be transposed, only reshaped
    """
    einsum_list_list: List[List[int]] = [[], [], []]
    counter = itertools.count(start=0)

    # Consturcting state indices
    einsum_dict: Dict[BaseState, List[int]] = {s: [] for s in state_objs}
    for s in state_objs:
        c = next(counter)
        einsum_dict[s].append(c)
        einsum_list_list[1].append(c)

    # Extra dimension, because vector is still a 2d matrix in jnp view
    ed = next(counter)
    einsum_list_list[1].append(ed)

    # Constructing operation indices
    for s in operator_objs:
        c = next(counter)
        einsum_list_list[0].append(c)
        einsum_dict[s].append(c)

    for s in operator_objs:
        einsum_list_list[0].append(einsum_dict[s][0])

    # Constructing resulting indices
    for s in state_objs:
        if s in operator_objs:
            einsum_list_list[2].append(einsum_dict[s][1])
        else:
            einsum_list_list[2].append(einsum_dict[s][0])
    einsum_list_list[2].append(ed)

    einsum_list_str: List[str] = [
        "".join([chr(97 + i) for i in s]) for s in einsum_list_list
    ]
    return f"{einsum_list_str[0]},{einsum_list_str[1]}->{einsum_list_str[2]}"


def apply_operator_matrix(state_objs: list, operator_objs: list) -> str:
    """
    Constructs an Einstein Sum string
    for multiplying an operator with a density matrix, where
    operator can be applied to the subspace.

    Parameters
    ----------
    state_objs: List[BaseState]
        List of all State objects which are in the product space
        The order should reflect the order in the tensoring
    operator_objs: List[BaseState]
        List of State objects on which the operator should be applied

    Returns
    -------
    str
        Einstein string that achieves the application

    Notes
    -----
    - The arrays should not be transposed, only reshaped

    Examples
    --------
    Suppose you have a state `original_state`, and you want to apply
    an operator to this state. You can reshape the state, apply the
    operator using `einsum`, and then reshape it back to the original
    dimensions.

    Example usage:

    >>> state = original_state.reshape(dims)
    >>> einsum = trace_out(state_objs, operator_objs)
    >>> new_state = jnp.einsum(einsum, operator, state, jnp.conj(operator))
    >>> new_state = new_state.reshape(new_dims)

    In this example:
    - `dims` and `new_dims` are the dimensions of the original and reshaped state.
    - `state_objs` is the list of state objects.
    - `operator_objs` is the list of operator objects.
    - `operator` is the operator to be applied.
    - `einsum` is the Einstein summation string generated by `trace_out`.
    """

    einsum_list_list: List[List[int]] = [[], [], [], []]
    einsum_dict: Dict["BaseState", List[int]] = {k: [] for k in state_objs}
    counter = itertools.count(start=0)

    # Create indices for the current states
    for _ in range(2):
        for s in state_objs:
            c = next(counter)
            einsum_dict[s].append(c)
            einsum_list_list[1].append(c)

    # Create indices for the first operator
    for s in operator_objs:
        c = next(counter)
        einsum_dict[s].append(c)
        einsum_list_list[0].append(c)

    for s in operator_objs:
        einsum_list_list[0].append(einsum_dict[s][0])

    # Create indices for the second operator
    for s in operator_objs:
        c = next(counter)
        einsum_list_list[2].append(c)
        einsum_dict[s].append(c)

    for s in operator_objs:
        einsum_list_list[2].append(einsum_dict[s][1])

    # Create indices for the outcome state

    for s in state_objs:
        if s in operator_objs:
            einsum_list_list[3].append(einsum_dict[s][2])
        else:
            einsum_list_list[3].append(einsum_dict[s][0])

    for s in state_objs:
        if s in operator_objs:
            einsum_list_list[3].append(einsum_dict[s][3])
        else:
            einsum_list_list[3].append(einsum_dict[s][1])

    einsum_list = ["".join([chr(97 + i) for i in s]) for s in einsum_list_list]
    return f"{einsum_list[0]},{einsum_list[1]},{einsum_list[2]}->{einsum_list[3]}"


def trace_out_vector(state_objs: list, states: list) -> str:
    """
    Produces an Einstein sum string. It's application traces out
    the states which are not included in the states list when
    the states are in vector form

    Parameters
    ----------
    state_objs: list
        List of all State objects which are in the product space
        The order should reflect the order in the tensoring
    states: List[BaseState]
        List of State objects which should not be traced out

    Notes
    -----
    - State should not be transposed, only reshaped
    """

    einsum_list_list: List[List[int]] = [[], []]
    c1 = itertools.count(start=0)
    for so in state_objs:
        if not so in states:
            c = next(c1)
            einsum_list_list[0].append(c)
        else:
            c = next(c1)
            einsum_list_list[0].append(c)
            einsum_list_list[1].append(c)
    c = next(c1)
    einsum_list_list[0].append(c)
    einsum_list_list[1].append(c)
    einsum_list = [[chr(97 + x) for x in string] for string in einsum_list_list]
    einsum_str = ["".join(s) for s in einsum_list]

    return f"{einsum_str[0]}->{einsum_str[1]}"


def trace_out_matrix(state_objs: list, states: list) -> str:
    """
    Produces an Einstein sum string. It's application traces out
    the states which are not included in the states list. Where
    the states are in matrix form.

    Parameters
    ----------
    state_objs: list
        List of all State objects which are in the product space
        The order should reflect the order in the tensoring
    states: List[BaseState]
        List of State objects which should not be traced out

    Notes
    -----
    - State should not be transposed, only reshaped
    """

    einsum_list_list: List[List[int]] = [[], []]
    counter = itertools.count(start=0)
    sum_out = next(counter)
    for _ in range(2):
        for so in state_objs:
            if not so in states:
                einsum_list_list[0].append(sum_out)
            else:
                c = next(counter)
                einsum_list_list[0].append(c)
                einsum_list_list[1].append(c)

    einsum_list = ["".join([chr(97 + i) for i in s]) for s in einsum_list_list]
    einsum_str = f"{einsum_list[0]}->{einsum_list[1]}"
    return einsum_str


def reorder_vector(state_objs: list, states: list) -> str:
    """
    Produces an Einstein sum string. It's application reorders
    the states in the the product state vector

    Parameters
    ----------
    state_objs: list
        List of all State objects which are in the product space
        The order should reflect the order in the tensoring
    states: List[BaseState]
        States in the new order

    Notes
    -----
    - State should not be transposed, only reshaped
    """
    einsum_dict: Dict["BaseState", int] = {s: -1 for s in state_objs}
    counter = itertools.count(start=0)
    # For the last index
    other = next(counter)
    einsum_list_list: List[List[int]] = [[], []]
    for s in state_objs:
        c = next(counter)
        einsum_list_list[0].append(c)
        einsum_dict[s] = c
    einsum_list_list[0].append(other)

    einsum_list_list[1] = [einsum_dict[s] for s in states]
    einsum_list_list[1].append(other)

    einsum_list = ["".join([chr(97 + s) for s in e]) for e in einsum_list_list]
    return f"{einsum_list[0]}->{einsum_list[1]}"


def reorder_matrix(state_objs: list, states: list) -> str:
    """
    Produces an Einstein sum string. It's application traces out
    the states which are not included in the states list when
    the states are in vector form

    Parameters
    ----------
    state_objs: list
        List of all State objects which are in the product space
        The order should reflect the order in the tensoring
    states: List[BaseState]
        List of State objects which should not be traced out

    Notes
    -----
    - State should not be transposed, only reshaped
    """
    einsum_list_list: List[List[int]] = [[], []]
    einsum_dict: Dict["BaseState", List[int]] = {s: [] for s in state_objs}
    counter = itertools.count(start=0)

    for _ in range(2):
        for s in state_objs:
            c = next(counter)
            einsum_list_list[0].append(c)
            einsum_dict[s].append(c)

    for i in range(2):
        for s in states:
            c = einsum_dict[s][i]
            einsum_list_list[1].append(c)

    einsum_list = ["".join([chr(97 + s) for s in e]) for e in einsum_list_list]
    return f"{einsum_list[0]}->{einsum_list[1]}"


def measure_vector(state_objs: list, states: list) -> str:
    """
    Produces an Einstein sum string. It's application exposes
    the listed states, so they could be measured.

    Parameters
    ----------
    state_objs: list
        List of all State objects which are in the product space
        The order should reflect the order in the tensoring
    states: List[BaseState]
        List of State objects which should be measured

    Notes
    -----
    - State should not be transposed, only reshaped
    """
    einsum_list_list: List[List[int]] = [[], []]
    einsum_dict: Dict["BaseState", List[int]] = {s: [] for s in state_objs}
    counter = itertools.count(start=0)

    for so in state_objs:
        c = next(counter)
        if so in states:
            einsum_list_list[1].append(c)
        einsum_list_list[0].append(c)

    # Accounting for the verical nature of vector
    c = next(counter)
    einsum_list_list[0].append(c)
    einsum_list_list[1].append(c)

    einsum_list = ["".join([chr(97 + s) for s in e]) for e in einsum_list_list]
    return f"{einsum_list[0]}->{einsum_list[1]}"


def measure_matrix(state_objs: list, states: list) -> str:
    """
    Produces an Einstein sum string. It's application exposes
    the listed states, so they could be measured.

    Parameters
    ----------
    state_objs: list
        List of all State objects which are in the product space
        The order should reflect the order in the tensoring
    states: List[BaseState]
        List of State objects which should be measured

    Notes
    -----
    - State should not be transposed, only reshaped
    """
    einsum_list_list: List[List[int]] = [[], []]
    einsum_dict: Dict["BaseState", List[int]] = {s: [] for s in state_objs}
    counter = itertools.count(start=0)

    for _ in range(2):
        for so in state_objs:
            c = next(counter)
            if so in states:
                einsum_list_list[1].append(c)
            einsum_list_list[0].append(c)

    einsum_list = ["".join([chr(97 + s) for s in e]) for e in einsum_list_list]
    return f"{einsum_list[0]}->{einsum_list[1]}"
