import os
from toolkit import conversion_toolkit
from toolkit.conversion_toolkit import FileType
import time
import json
import argparse

modules_location = os.path.abspath("./modules")
external_modules_location = os.path.abspath("./downloaded_programs")
toolkit_location = os.path.abspath("./toolkit")


def _stage_output_path(
    working_dir,
    stage_number,
    method,
):
    return f"{working_dir}/{stage_number}_{method}"


def run_pipeline(input_network, working_dir, final_clustering, method_arr):
    """This is a generic method that takes in an input network and runs all the methods in method_arr
    The output of the previous stage networks and clusterings get fed to the next stages input
    """
    previous_stage_network = input_network
    previous_stage_clustering = None
    for stage_number, method in enumerate(method_arr):
        print(f"> Stage {stage_number + 1} started.")

        previous_stage_network, previous_stage_clustering = run_method(
            method=method,
            method_params=method_arr[method],
            current_network=previous_stage_network,
            current_clustering=previous_stage_clustering,
            working_dir=working_dir,
            stage_number=stage_number + 1,
        )

        print(f"> Stage {stage_number + 1} complete.\n")

    os.system(f"cp {previous_stage_clustering} {final_clustering}")


def run_method(
    method,
    method_params,
    current_network,
    current_clustering,
    working_dir,
    stage_number,
):
    """This method showcases different example commands for different programs."""
    print(f">> Running {method} at stage {stage_number}")
    print(f">> Current network: {current_network}")
    print(f">> Current clustering: {current_clustering}")
    print(f">> Working directory: {working_dir}")
    print(f">> Method parameters: {method_params}")

    if method == "leiden-mod":
        leiden_location = f"{modules_location}/run_leiden.py"
        stage_output = _stage_output_path(working_dir, stage_number, method)
        leiden_output = f"{stage_output}.csv"
        os.system(
            f"python {leiden_location} --edgelist {current_network} --output {leiden_output} --model mod"
        )
        return current_network, leiden_output

    elif method == "leiden-cpm":
        leiden_location = f"{modules_location}/run_leiden.py"
        stage_output = _stage_output_path(working_dir, stage_number, method)
        leiden_output = f"{stage_output}.csv"
        os.system(
            f"python {leiden_location} --edgelist {current_network} --output {leiden_output} --model cpm --resolution {method_params['res']}"
        )
        return current_network, leiden_output

    elif method == "ikc":
        ikc_location = f"{modules_location}/run_ikc.py"
        stage_output = _stage_output_path(working_dir, stage_number, method)
        ikc_output = f"{stage_output}.csv"
        command = (
            f"python {ikc_location} --edgelist {current_network} --output {ikc_output}"
        )

        # Argument
        if "k" in method_params:
            command = f"{command} -k {method_params['k']}"
        os.system(command)
        return current_network, ikc_output

    elif method == "infomap":
        infomap_location = f"{modules_location}/run_infomap.py"
        stage_output = _stage_output_path(working_dir, stage_number, method)
        infomap_output = f"{stage_output}.csv"
        os.system(
            f"python {infomap_location} --edgelist {current_network} --output {infomap_output}"
        )
        return current_network, infomap_output

    elif method == "sbm":
        sbm_location = f"{modules_location}/run_sbm.py"
        stage_output = _stage_output_path(working_dir, stage_number, method)
        sbm_output = f"{stage_output}.csv"

        # Argument
        command = (
            f"python {sbm_location} --edgelist {current_network} --output {sbm_output}"
        )
        if "block_state" in method_params:
            command = f"{command} -b {method_params['block_state']}"
        else:
            raise ValueError(
                f"pipeline stage {stage_number}: block_state is required for SBM"
            )

        os.system(command)
        return current_network, sbm_output

    elif method == "wcc":
        wcc_location = f"{external_modules_location}/constrained_clustering"
        stage_output = _stage_output_path(working_dir, stage_number, method)
        wcc_output = f"{stage_output}.csv"

        # Argument
        command = f"{wcc_location} MincutOnly --edgelist {current_network} --existing-clustering {current_clustering} --output-file {wcc_output} --num-processors 1 --log-file {stage_output}.log --log-level 1"

        if "connectedness-criterion" in method_params:
            command = f"{command} -b {method_params['criterion']}"
        else:
            raise ValueError(
                f"pipeline stage {stage_number}: criterion is required for WCC"
            )

        os.system(command)
        return current_network, wcc_output

    elif method == "cc":
        cc_location = f"{external_modules_location}/constrained_clustering"
        stage_output = _stage_output_path(working_dir, stage_number, method)
        cc_output = f"{stage_output}.csv"
        os.system(
            f"{cc_location} MincutOnly --edgelist {current_network} --existing-clustering {current_clustering} --output-file {cc_output} --num-processors 1 --log-file {stage_output}.log --connectedness-criterion 0 --log-level 1"
        )
        return current_network, cc_output

    # TODO: AOC should only be called when there is IKC in the previous stage
    elif method == "aoc":
        # aoc_location = f"{external_modules_location}/aoc"
        stage_output = _stage_output_path(working_dir, stage_number, method)
        aoc_output = f"{stage_output}.csv"

        aoc_tmp_network = f"{stage_output}.tmp.edgelist"
        aoc_tmp_cluster = f"{stage_output}.tmp.clustering"

        # Need to convert input files
        conversion_toolkit.convert_to(current_network, aoc_tmp_network, " ", False)
        conversion_toolkit.convert_to(current_clustering, aoc_tmp_cluster, " ", False)

        # Argument
        command = f"aocluster augment -g {aoc_tmp_network} -c {aoc_tmp_cluster} --candidates all -o {aoc_output} -a 0"
        if "m" in method_params:
            command = f"{command} -m {method_params['m']}"
        else:
            raise ValueError(f"pipeline stage {stage_number}: m is required for AOC")

        os.system(
            # f"aocluster augment -g {aoc_tmp_network} -c {aoc_tmp_cluster} -m k{2} --candidates all --legacy-cid-nid-order --strategy legacy -o {aoc_output} -a 0"
            command
        )

        conversion_toolkit.convert_to_canonical(
            aoc_output, aoc_output, FileType.CLUSTER
        )

        # Remove temporary files
        os.remove(aoc_tmp_network)
        os.remove(aoc_tmp_cluster)

        return current_network, aoc_output

    # DSC related
    elif method == "flow-iter" or method == "flow":
        flow_iter_location = f"{external_modules_location}/{method}"
        stage_output = _stage_output_path(working_dir, stage_number, method)
        flow_iter_output_cluster = f"{stage_output}.csv"
        flow_iter_output_density = f"{stage_output}.density.csv"

        flow_iter_tmp_network = f"{stage_output}.tmp.input.edgelist"

        # Remove header from input edgelist
        conversion_toolkit.convert_to(
            current_network, flow_iter_tmp_network, "\t", False
        )

        os.system(
            f"{flow_iter_location} {flow_iter_tmp_network} {flow_iter_output_cluster} {flow_iter_output_density}"
        )

        # Add header to the output cluster
        conversion_toolkit.convert_to_canonical(
            flow_iter_output_cluster, flow_iter_output_cluster, FileType.CLUSTER
        )

        # TODO: for now, leave density unchanged since it is not part of our standard specification

        # Remove temporary files
        os.remove(flow_iter_tmp_network)

        return current_network, flow_iter_output_cluster

    elif method == "fista-int" or method == "fista-frac":
        fista_location = f"{external_modules_location}/{method}"
        stage_output = _stage_output_path(working_dir, stage_number, method)
        fista_output_cluster = f"{stage_output}.csv"
        fista_output_density = f"{stage_output}.density.csv"

        fista_tmp_network = f"{stage_output}.tmp.input.edgelist"

        # Remove header from input edgelist
        conversion_toolkit.convert_to(current_network, fista_tmp_network, "\t", False)

        # Argument
        command = f"{fista_location} {fista_tmp_network} {fista_output_cluster} {fista_output_density}"
        if "niters" in method_params:
            command = f"{command} -niters {method_params['niters']}"

        os.system(command)

        # Add header to the output cluster
        conversion_toolkit.convert_to_canonical(
            fista_output_cluster, fista_output_cluster, FileType.CLUSTER
        )

        # TODO: for now, leave density unchanged since it is not part of our standard specification

        # Remove temporary files
        os.remove(fista_tmp_network)

        return current_network, fista_output_cluster

    # CM related
    elif method == "cm":
        cm_directory = f"{external_modules_location}/cm_pipeline/"
        stage_output = _stage_output_path(working_dir, stage_number, method)
        cm_output_cluster = os.path.abspath(f"{stage_output}.csv")

        cm_tmp_network = os.path.abspath(f"{stage_output}.tmp.input.edgelist")
        if current_clustering is not None:
            cm_tmp_cluster = os.path.abspath(f"{stage_output}.tmp.input.cluster")

        # Remove header from input edgelist (& cluster if available)
        conversion_toolkit.convert_to(current_network, cm_tmp_network, "\t", False)
        if current_clustering is not None:
            conversion_toolkit.convert_to(
                current_clustering, cm_tmp_cluster, "\t", False
            )

        current_directory = os.getcwd()
        os.chdir(cm_directory)

        # Arguments
        command = (
            f"python -m hm01.cm --input {cm_tmp_network} --output {cm_output_cluster}"
        )

        if current_clustering is not None:
            command = f"{command} --existing-clustering {cm_tmp_cluster}"

        if "resolution" in method_params:
            resolution = method_params["resolution"]
            command = f"{command} --resolution {resolution}"

        if "clusterer" in method_params:
            clusterer = method_params["clusterer"]
            command = f"{command} --clusterer {clusterer}"
        else:
            raise ValueError(
                f"pipeline stage {stage_number}: clusterer is required for CM"
            )

        if "quiet" in method_params:
            command = f"{command} --quiet"
        if "no-prune" in method_params:
            command = f"{command} --no-prune"
        if "k" in method_params:
            k = method_params["k"]
            command = f"{command} --k {k}"
        if "threshold" in method_params:
            threshold = method_params["threshold"]
            command = f"{command} --threshold {threshold}"
        if "nprocs" in method_params:
            nprocs = method_params["nprocs"]
            command = f"{command} --nprocs {nprocs}"
        if "clusterer_file" in method_params:
            clusterer_file = method_params["clusterer_file"]
            command = f"{command} --clusterer_file {clusterer_file}"
        if "clusterer_args" in method_params:
            clusterer_args = method_params["clusterer_args"]
            command = f"{command} --clusterer_args {clusterer_args}"
        if "existing-clustering" in method_params:
            existing_clustering = method_params["existing-clustering"]
            command = f"{command} --existing-clustering {existing_clustering}"

        os.system(command)
        print(command)

        os.chdir(current_directory)

        # Add header to the output cluster
        conversion_toolkit.convert_to_canonical(
            cm_output_cluster, cm_output_cluster, FileType.CLUSTER
        )

        # Remove temporary files
        os.remove(cm_tmp_network)
        if current_clustering is not None:
            os.remove(cm_tmp_cluster)

        return current_network, cm_output_cluster

    # elif method == "cm-pipeline":
    #     cm_location = f"{external_modules_location}/run_cm_pipeline.py"
    #     pass


# TODO: this should be expanded to check for more dependencies
def check_dependencies(stages: dict):
    # aoc should only work with ikc
    if "aoc" in stages:
        if "ikc" not in stages:
            raise ValueError(f"AOC requires IKC in the previous stage")
        else:
            if "m" not in stages["aoc"]:
                stages["aoc"]["m"] = f"k{stages['ikc']['k']}"


""" Step 1: specify input network, working directory, and final output clustering name"""
""" Step 2: specify the methods, their parameters, and their order
    List of possible method names for any stage that starts with an input network only:
        leiden-cpm (needs parameter called "res" for the resolution value)
        leiden-mod
        ikc
        infomap
        TO BE EXPANDED

    List of possible method names for any stage that starts with an input network and input clustering:
        wcc
        cc
        aoc (ikc-only)
        dsc (flow, flow-iter, fista, fista-iter)
        cm
        TO BE EXPANDED
"""

# example pipeline
method_arr = {
    # "ikc": {
    #     "k": 2,
    # },
    # "infomap": {},
    # # "leiden-cpm": {
    # #     "res": 0.1,
    # # },
    # # "aoc": {
    # #     "m": "k2",
    # # },
    # "wcc": {
    #     "threshold": "1log10",  # c, xlog_y(n)
    # },
    "cm": {"clusterer": "leiden", "resolution": 0.01}
}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("input_pipeline", type=str, help="Input pipeline file")
    parser.add_argument("input_network", type=str, help="Input network edgelist")
    parser.add_argument(
        "-w",
        "--working-dir",
        type=str,
        required=False,
        default=None,
        help="Path to the working dir",
    )
    parser.add_argument(
        "-o",
        "--output-file",
        type=str,
        required=False,
        default=None,
        help="Path to the final output clustering file",
    )

    args = parser.parse_args()

    # Argument processing
    input_pipeline = os.path.abspath(args.input_pipeline)
    input_network = os.path.abspath(args.input_network)

    if args.working_dir is None:
        working_dir = f"./outputs/working_dir-{time.time()}"
    else:
        working_dir = args.working_dir
    working_dir = os.path.abspath(working_dir)

    if args.output_file is None:
        output_file = f"{working_dir}/final_clustering.csv"
    else:
        output_file = args.output_file
    output_file = os.path.abspath(output_file)

    # Setup
    os.makedirs(working_dir, exist_ok=True)

    # Read in pipeline
    with open(input_pipeline, "r") as pipeline:
        method_arr = json.load(pipeline)

    # Check dependencies
    check_dependencies(method_arr)

    # Run pipeline
    run_pipeline(input_network, working_dir, output_file, method_arr)
