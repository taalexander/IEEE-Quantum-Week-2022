"""Helper methods for running OpenQASM3 programs with the qiskit_ibm_runtime.

(C) Copyright IBM 2021.

"""

from typing import List, Optional, Union

from qiskit import QuantumCircuit, qasm3

from qiskit.providers.ibmq import RunnerResult

from qiskit_ibm_runtime import RuntimeJob, IBMBackend

QASM3_INPUT = Union[QuantumCircuit, str]

Program = Union[QuantumCircuit, str]
def run_openqasm3(
    circuits: Union[Program, List[Program]],
    backend: IBMBackend,
    verbose: bool = True,
    draw: bool = True,
    runtime_image: Optional[str] = None,
    merge_circuits: bool = True,
    init_circuit: Optional[QuantumCircuit] = None,
    init_num_resets: int = 3,
    init_delay: float = 0.,

    **run_config,
) -> List[RuntimeJob]:
    """Run a list of Qiskit circuits or QASM3 strings through the Qiskit runtime.

    Args:
        circuits: QuantumCircuit or qasm3 source strings to run.
        backend: Backend to run on.
        verbose: Print out execution information
        draw: Draw the circuit.
        runtime_image: The Qiskit runtime base image to launch the runtime from. If not set this
            will select the image that is automatically compatible with the latest Qiskit
            release. If you are using a different branch of Qiskit you may need to select another
            image such as "terra-main:latest". This is because Qiskit Terra's QPY is used to
            serialize and deserialize circuits to the runtime service. Having different versions
            of Qiskit Terra on your local machine compared to the remote Qiskit Runtime image
            may result in serdes incompatibilities. Note that not all accounts
            are authorized to select a different image - if this is an issue for you contact
            #vt-qiskit-runtime.
        merge_circuits: Whether to merge multiple QuantumCircuits into one single QuantumCircuit
            containing each individual circuit separated by an initialization circuit.
            This will greatly improve the performance of your runtime program and should
            almost always be used. The default initialization circuit is a series of qubit resets
            (the number of which may be configured with "init_num_resets" ) on qubits used
            in your experiment followed by a relaxation delay (Which may be specified with
            "init_delay". You may also provide your own initialization circuit through "init_circuit"
        init_num_resets: The number of qubit resets to insert before each circuit execution.
        init_delay: The number of microseconds of delay to insert before each circuit execution.
        run_config: Extra compilation / executions options such as the number of shots.

    """

    if isinstance(circuits, (QuantumCircuit, str)):
        circuits = [circuits]

    config = backend.configuration()

    for circuit_idx, circuit in enumerate(circuits):
        if verbose:
            if isinstance(circuit, QuantumCircuit):
                print(f"======={circuit.name}=======")
                print("=======QASM3======")
                print(qasm3.Exporter(includes=[], basis_gates=config.basis_gates).dumps(circuit))
                print("==================")
                if draw:
                    print(circuit.draw(idle_wires=False))
                    print("==================")
            else:
                print("=======QASM3======")
                print(circuit)

    runtime_params = {
        "circuits": circuits,
        "run_config": run_config,
        "merge_circuits": merge_circuits,
        "init_num_resets": init_num_resets,
        "init_delay": init_delay,
        "init_circuit": init_circuit,
        "skip_transpilation": True,
    }
    options = {
        "backend_name": backend.name,
        "image": runtime_image,
    }
    job = backend.service.run(
        program_id="qasm3-runner",
        options=options,
        inputs=runtime_params,
        result_decoder=RunnerResult,
    )
    if verbose:
        print(f"Running: {job.job_id}")

    if verbose:
        result = job.result()
        for circuit_idx, circuit in enumerate(circuits):
            counts = result.get_counts(circuit_idx)
            if isinstance(circuit, QuantumCircuit):
                print(f"======={circuit.name}=======")
            else:
                print(f"==============")
            print (counts)

    return job

