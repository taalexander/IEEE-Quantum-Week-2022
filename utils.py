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
    max_execution_time: int = 900,
    program_id: str = "qasm3-runner",
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
        max_execution_time: Maximum execution time for the runtime program.
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
                    print(circuit.draw(idle_wires=False, output="text"))
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
        program_id=program_id,
        options=options,
        inputs=runtime_params,
        result_decoder=RunnerResult,
        max_execution_time=max_execution_time
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



# Jupyter widget for Qiskit Runtime
import types
import math
from IPython.display import display
import matplotlib.pyplot as plt
import ipywidgets as widgets
from qiskit.exceptions import QiskitError
from qiskit.visualization.gate_map import plot_gate_map, plot_error_map


MONTH_NAMES = {
    1: "Jan.",
    2: "Feb.",
    3: "Mar.",
    4: "Apr.",
    5: "May",
    6: "June",
    7: "July",
    8: "Aug.",
    9: "Sept.",
    10: "Oct.",
    11: "Nov.",
    12: "Dec.",
}


def _load_jobs_data(self, change):
    """Loads backend jobs data"""
    if change["new"] == 4 and not self._did_jobs:
        self._did_jobs = True
        year = widgets.Output(
            layout=widgets.Layout(display="flex-inline", align_items="center", min_height="400px")
        )

        month = widgets.Output(
            layout=widgets.Layout(display="flex-inline", align_items="center", min_height="400px")
        )

        week = widgets.Output(
            layout=widgets.Layout(display="flex-inline", align_items="center", min_height="400px")
        )

        self.children[4].children = [year, month, week]
        self.children[4].set_title(0, "Year")
        self.children[4].set_title(1, "Month")
        self.children[4].set_title(2, "Week")
        self.children[4].selected_index = 1


def _backend_monitor(backend):
    """A private function to generate a monitor widget
    for a IBMQ backend repr.
    Args:
        backend (IBMBackend): The backend.
    Raises:
        QiskitError: Input is not an IBMBackend
    """
    if not isinstance(backend, IBMBackend):
        raise QiskitError("Input variable is not of type IBMQBackend.")
    title_style = "style='color:#ffffff;background-color:#000000;padding-top: 1%;"
    title_style += "padding-bottom: 1%;padding-left: 1%; margin-top: 0px'"
    title_html = f"<h1 {title_style}>{backend.name}</h1>"

    details = [config_tab(backend)]

    tab_contents = ["Configuration"]

    # Empty jobs tab widget
    jobs = widgets.Tab(layout=widgets.Layout(max_height="620px"))

    if not backend.configuration().simulator:
        tab_contents.extend(["Qubit Properties", "Multi-Qubit Gates", "Error Map"])

        details.extend([qubits_tab(backend), gates_tab(backend), detailed_map(backend)])

    tabs = widgets.Tab(layout=widgets.Layout(overflow_y="scroll"))
    tabs.children = details
    for i in range(len(details)):
        tabs.set_title(i, tab_contents[i])

    # Make backend accessible to tabs widget
    tabs._backend = backend
    tabs._did_jobs = False
    tabs._update = types.MethodType(_load_jobs_data, tabs)

    tabs.observe(tabs._update, names="selected_index")

    title_widget = widgets.HTML(value=title_html, layout=widgets.Layout(margin="0px 0px 0px 0px"))

    bmonitor = widgets.VBox(
        [title_widget, tabs],
        layout=widgets.Layout(
            border="4px solid #000000", max_height="650px", min_height="650px", overflow_y="hidden"
        ),
    )
    display(bmonitor)


def config_tab(backend):
    """The backend configuration widget.
    Args:
        backend (IBMQBackend | FakeBackend): The backend.
    Returns:
        grid: A GridBox widget.
    """
    status = backend.status().to_dict()
    config = backend.configuration().to_dict()

    config_dict = {**status, **config}

    upper_list = ["n_qubits"]

    if "quantum_volume" in config.keys():
        if config["quantum_volume"]:
            upper_list.append("quantum_volume")

    upper_list.extend(
        [
            "operational",
            "status_msg",
            "pending_jobs",
            "backend_version",
            "basis_gates",
            "max_shots",
            "max_experiments",
        ]
    )

    lower_list = list(set(config_dict.keys()).difference(upper_list))
    # Remove gates because they are in a different tab
    lower_list.remove("gates")
    # Look for hamiltonian
    if "hamiltonian" in lower_list:
        htex = config_dict["hamiltonian"]["h_latex"]
        config_dict["hamiltonian"] = "$$%s$$" % htex

    upper_str = "<table>"
    upper_str += """<style>
table {
    border-collapse: collapse;
    width: auto;
}
th, td {
    text-align: left;
    padding: 8px;
}
tr:nth-child(even) {background-color: #f6f6f6;}
</style>"""

    footer = "</table>"

    # Upper HBox widget data

    upper_str += "<tr><th>Property</th><th>Value</th></tr>"
    for key in upper_list:
        upper_str += "<tr><td><font style='font-weight:bold'>{}</font></td><td>{}</td></tr>".format(
            key,
            config_dict[key],
        )
    upper_str += footer

    upper_table = widgets.HTMLMath(
        value=upper_str, layout=widgets.Layout(width="100%", grid_area="left")
    )

    image_widget = widgets.Output(
        layout=widgets.Layout(
            display="flex-inline",
            grid_area="right",
            padding="10px 10px 10px 10px",
            width="auto",
            max_height="325px",
            align_items="center",
        )
    )

    if not config["simulator"]:
        with image_widget:
            qubit_size = 24
            if config["n_qubits"] > 20:
                qubit_size = 34
            gate_map = plot_gate_map(backend, qubit_size=qubit_size)
            display(gate_map)
        plt.close(gate_map)

    lower_str = "<table>"
    lower_str += """<style>
table {
    border-collapse: collapse;
    width: auto;
}
th, td {
    text-align: left;
    padding: 8px;
}
tr:nth-child(even) {background-color: #f6f6f6;}
</style>"""
    lower_str += "<tr><th></th><th></th></tr>"
    for key in lower_list:
        if key != "name":
            lower_str += f"<tr><td>{key}</td><td>{config_dict[key]}</td></tr>"
    lower_str += footer

    lower_table = widgets.HTMLMath(
        value=lower_str, layout=widgets.Layout(width="auto", grid_area="bottom")
    )

    grid = widgets.GridBox(
        children=[upper_table, image_widget, lower_table],
        layout=widgets.Layout(
            grid_template_rows="auto auto",
            grid_template_columns="31% 23% 23% 23%",
            grid_template_areas="""
                               "left right right right"
                               "bottom bottom bottom bottom"
                               """,
            grid_gap="0px 0px",
        ),
    )

    return grid


def qubits_tab(backend):
    """The qubits properties widget
    Args:
        backend (IBMQBackend | FakeBackend): The backend.
    Returns:
        VBox: A VBox widget.
    """
    props = backend.properties()

    header_html = "<div><font style='font-weight:bold'>{key}</font>: {value}</div>"
    update_date = props.last_update_date.strftime("%a %d %B %Y at %H:%M %Z")
    header_html = header_html.format(key="last_update_date", value=update_date)

    update_date_widget = widgets.HTML(value=header_html)

    qubit_html = "<table>"
    qubit_html += """<style>
table {
    border-collapse: collapse;
    width: auto;
}
th, td {
    text-align: left;
    padding: 8px;
}
tr:nth-child(even) {background-color: #f6f6f6;}
</style>"""

    qubit_html += "<tr><th></th><th>Frequency</th><th>T1</th><th>T2</th>"
    qubit_footer = "</table>"

    gate_error_title = ""

    for index, qubit_data in enumerate(props.qubits):
        name = "Q%s" % index
        gate_data = [gate for gate in props.gates if gate.qubits == [index]]

        cal_data = dict.fromkeys(["T1", "T2", "frequency", "readout_error"], "Unknown")
        for nduv in qubit_data:
            if nduv.name in cal_data:
                cal_data[nduv.name] = str(round(nduv.value, 5)) + " " + nduv.unit

        gate_names = []
        gate_error = []
        for gd in gate_data:
            if gd.gate in ["id"]:
                continue
            try:
                gate_error.append(str(round(props.gate_error(gd.gate, index), 5)))
                gate_names.append(gd.gate.upper())
            except QiskitError:
                pass

        if not gate_error_title:
            for gname in gate_names:
                gate_error_title += f"<th>{gname}</th>"
            qubit_html += gate_error_title + "<th>Readout error</th></tr>"

        qubit_html += f"<tr><td><font style='font-weight:bold'>{name}</font></td>"
        qubit_html += (
            f"<td>{cal_data['frequency']}</td><td>{cal_data['T1']}</td><td>{cal_data['T2']}</td>"
        )
        for gerror in gate_error:
            qubit_html += f"<td>{gerror}</td>"
        qubit_html += f"<td>{cal_data['readout_error']}</td>"

    qubit_html += qubit_footer

    qubit_widget = widgets.HTML(value=qubit_html)

    out = widgets.VBox([update_date_widget, qubit_widget])

    return out


def gates_tab(backend):
    """The multiple qubit gate error widget.
    Args:
        backend (IBMQBackend | FakeBackend): The backend.
    Returns:
        VBox: A VBox widget.
    """
    props = backend.properties()

    multi_qubit_gates = [g for g in props.gates if len(g.qubits) > 1]

    header_html = "<div><font style='font-weight:bold'>{key}</font>: {value}</div>"
    header_html = header_html.format(key="last_update_date", value=props.last_update_date)

    update_date_widget = widgets.HTML(value=header_html, layout=widgets.Layout(grid_area="top"))

    gate_html = "<table>"
    gate_html += """<style>
table {
    border-collapse: collapse;
    width: auto;
}
th, td {
    text-align: left;
    padding: 8px;
}
tr:nth-child(even) {background-color: #f6f6f6;};
</style>"""

    gate_html += "<tr><th></th><th>Type</th><th>Gate error</th></tr>"
    gate_footer = "</table>"

    # Split gates into two columns
    left_num = math.ceil(len(multi_qubit_gates) / 3)
    mid_num = math.ceil((len(multi_qubit_gates) - left_num) / 2)

    left_table = gate_html

    for qub in range(left_num):
        gate = multi_qubit_gates[qub]
        qubits = gate.qubits
        ttype = gate.gate
        error = round(props.gate_error(gate.gate, qubits), 5)

        left_table += "<tr><td><font style='font-weight:bold'>%s</font>"
        left_table += "</td><td>%s</td><td>%s</td></tr>"
        left_table = left_table % (f"{ttype}{qubits[0]}_{qubits[1]}", ttype, error)
    left_table += gate_footer

    middle_table = gate_html

    for qub in range(left_num, left_num + mid_num):
        gate = multi_qubit_gates[qub]
        qubits = gate.qubits
        ttype = gate.gate
        error = round(props.gate_error(gate.gate, qubits), 5)

        middle_table += "<tr><td><font style='font-weight:bold'>%s</font>"
        middle_table += "</td><td>%s</td><td>%s</td></tr>"
        middle_table = middle_table % (f"{ttype}{qubits[0]}_{qubits[1]}", ttype, error)
    middle_table += gate_footer

    right_table = gate_html

    for qub in range(left_num + mid_num, len(multi_qubit_gates)):
        gate = multi_qubit_gates[qub]
        qubits = gate.qubits
        ttype = gate.gate
        error = round(props.gate_error(gate.gate, qubits), 5)

        right_table += "<tr><td><font style='font-weight:bold'>%s</font>"
        right_table += "</td><td>%s</td><td>%s</td></tr>"
        right_table = right_table % (f"{ttype}{qubits[0]}_{qubits[1]}", ttype, error)
    right_table += gate_footer

    left_table_widget = widgets.HTML(value=left_table, layout=widgets.Layout(grid_area="left"))
    middle_table_widget = widgets.HTML(
        value=middle_table, layout=widgets.Layout(grid_area="middle")
    )
    right_table_widget = widgets.HTML(value=right_table, layout=widgets.Layout(grid_area="right"))

    grid = widgets.GridBox(
        children=[update_date_widget, left_table_widget, middle_table_widget, right_table_widget],
        layout=widgets.Layout(
            grid_template_rows="auto auto",
            grid_template_columns="33% 33% 33%",
            grid_template_areas="""
                                                   "top top top"
                                                   "left middle right"
                                                   """,
            grid_gap="0px 0px",
        ),
    )

    return grid


def detailed_map(backend):
    """Widget for displaying detailed noise map.
    Args:
        backend (IBMQBackend | FakeBackend): The backend.
    Returns:
        GridBox: Widget holding noise map images.
    """
    error_widget = widgets.Output(
        layout=widgets.Layout(display="flex-inline", align_items="center")
    )
    with error_widget:
        display(plot_error_map(backend, figsize=(11, 9), show_title=False))
    return error_widget





from IPython import get_ipython

_IP = get_ipython()
HTML_FORMATTER = _IP.display_formatter.formatters["text/html"]
# Make _backend_monitor the html repr for IBM Q backends
HTML_FORMATTER.for_type(IBMBackend, _backend_monitor)

