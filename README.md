# IEEE Quantum Week 2022 Tutorial - TUT19 — Running Quantum Error Correction with IBM Quantum Services

To get started please see the [Hello IEEE notebook](./hello-ieee.ipynb). The tutorial itself is found in this [tutorial notebook](./tutorial.ipynb).

**Presenters**: @ehchen, @mbhealy, @taalexander

**Request Access**: thomas.a.alexander@ibm.com (A-M), mbhealy@ibm.com (N-Z)

**Location**: Omni Interlocken Hotel, Broomfield, Colorado, USA

**Room**: Ponderosa

**Date**: September 23rd, 2022

**Abstract**: All approaches to constructing and controlling a quantum computer are susceptible to errors that modify the target quantum state. On existing hardware, this limits the output fidelity of most quantum algorithms and prevents successfully executing most quantum algorithms. Quantum error correction codes, like their classical counterparts, enable the operation of high fidelity ‘logical‘ qubits encoded within collections of noisy and imperfect ‘physical‘ qubits. However, real-time error correction requires dynamic control of program flow during execution. That is to say, future operations on qubits must be conditioned on the results of measurements of specially designated qubits (such as flag or ancilla qubits) in most error correction algorithms. These measurement results can then be used to conditionally correct the state of the logical qubit. These decisions must occur within the lifetime of the computer’s qubits so that they may impact the quantum system before it decoheres. In this tutorial, we will introduce attendees to the basics of quantum error correction alongside OpenQASM3, a programming language that provides the features necessary to achieve quantum advantage using near-term quantum computers. We will then provide a high-level overview of the hardware and software requirements needed to implement dynamic control flow and quantum error correction. Finally, attendees will be taught how to write and run programs containing dynamic control flow and implement quantum error correction using real quantum systems provided through IBM Quantum Services and Qiskit.
Tutorial attendees should register with IBM Quantum platform, install Qiskit (locally or using the IBM Quantum Lab) and complete the Getting Started with Qiskit tutorial to prepare for the session. The tutorial content will consist of material of 20% beginner, 70% intermediate, and 10% advanced experience levels.

**Related tutorial**: Drew Vandeth, Andrew Cross and James Wootton's [Tutorial 26 on Thursday, September 22nd.](https://github.com/qiskit-community/qiskit-qec/blob/main/docs/tutorials/QEC_Framework_IEEE_2022.ipynb)
