from messthaler_wulff.graph import UniformNeighborhood

square = UniformNeighborhood.from_basis([
    [1, 0],
    [0, 1]])

cubic = UniformNeighborhood.from_basis([
    [1, 0, 0],
    [0, 1, 0],
    [0, 0, 1]])

triangular = UniformNeighborhood.from_basis([
    [1, 0],
    [1, 1],
    [0, 1]])

fcc = UniformNeighborhood.from_basis([
    (1, 0, 0), (0, 1, 0), (0, 0, 1),
    (-1, 0, 1), (1, -1, 0), (0, 1, -1)])

common = (square, cubic, triangular, fcc)
