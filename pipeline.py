import os
from toolkit import conversion_toolkit

modules_location = "./modules"
external_modules_location = "./downloaded_programs"
toolkit_location = "./toolkit"


def _construct_output_path(working_dir, stage_number, method):
    return f"{working_dir}/{stage_number}_{method}.csv"


def run_pipeline(input_network, working_dir, final_clustering, method_arr):
    """This is a generic method that takes in an input network and runs all the methods in method_arr
    The output of the previous stage networks and clusterings get fed to the next stages input
    """
    previous_stage_network = input_network
    previous_stage_clustering = None
    for stage_number, method in enumerate(method_arr):
        print(f"> Stage {stage_number} started.")

        previous_stage_network, previous_stage_clustering = run_method(
            method=method,
            method_params=method_arr[method],
            current_network=previous_stage_network,
            current_clustering=previous_stage_clustering,
            working_dir=working_dir,
            stage_number=stage_number,
        )

        print(f"> Stage {stage_number} complete.\n")

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
        leiden_output = f"{working_dir}/{stage_number}_{method}.csv"
        os.system(
            f"python {leiden_location} --edgelist {current_network} --output {leiden_output} --model mod"
        )
        return current_network, leiden_output

    elif method == "leiden-cpm":
        leiden_location = f"{modules_location}/run_leiden.py"
        leiden_output = f"{working_dir}/{stage_number}_{method}.csv"
        os.system(
            f"python {leiden_location} --edgelist {current_network} --output {leiden_output} --model cpm --resolution {method_params['res']}"
        )
        return current_network, leiden_output

    elif method == "ikc":
        ikc_location = f"{modules_location}/run_ikc.py"
        ikc_output = f"{working_dir}/{stage_number}_{method}.csv"
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
        infomap_output = f"{working_dir}/{stage_number}_{method}.csv"
        os.system(
            f"python {infomap_location} --edgelist {current_network} --output {infomap_output}"
        )
        return current_network, infomap_output

    elif method == "wcc":
        wcc_location = f"{external_modules_location}/constrained_clustering"
        wcc_output = f"{working_dir}/{stage_number}_{method}.csv"
        os.system(
            f"{wcc_location} MincutOnly --edgelist {current_network} --existing-clustering {current_clustering} --output-file {wcc_output} --num-processors 1 --log-file {working_dir}/{stage_number}.log --connectedness-criterion 1 --log-level 1"
        )
        return current_network, wcc_output

    elif method == "cc":
        cc_location = f"{external_modules_location}/constrained_clustering"
        cc_output = f"{working_dir}/{stage_number}_{method}.csv"
        os.system(
            f"{cc_location} MincutOnly --edgelist {current_network} --existing-clustering {current_clustering} --output-file {cc_output} --num-processors 1 --log-file {working_dir}/{stage_number}.log --connectedness-criterion 0 --log-level 1"
        )
        return current_network, cc_output

    # TODO: AOC should only be called when there is IKC in the previous stage
    elif method == "aoc":
        # aoc_location = f"{external_modules_location}/aoc"
        aoc_output = _construct_output_path(working_dir, stage_number, method)

        aoc_tmp_network = f"{aoc_output}.tmp.edgelist"
        aoc_tmp_cluster = f"{aoc_output}.tmp.clustering"

        # Need to convert input files
        conversion_toolkit.convert_to(current_network, aoc_tmp_network, " ", False)
        conversion_toolkit.convert_to(current_clustering, aoc_tmp_cluster, " ", False)

        # Argument
        command = f"aocluster augment -g {aoc_tmp_network} -c {aoc_tmp_cluster} --candidates all -o {aoc_output} -a 0"
        if "m" in method_params:
            command = f"{command} -m {method_params['m']}"

        os.system(
            # f"aocluster augment -g {aoc_tmp_network} -c {aoc_tmp_cluster} -m k{2} --candidates all --legacy-cid-nid-order --strategy legacy -o {aoc_output} -a 0"
            command
        )

        conversion_toolkit.convert_to(
            aoc_output, aoc_output, "\t", ["node_id", "cluster_id"]
        )

        # Remove temporary files
        os.remove(aoc_tmp_network)
        os.remove(aoc_tmp_cluster)

        return current_network, aoc_output


""" Step 1: specify input network, working directory, and final output clustering name"""
input_network = "./inputs/network.csv"  # user to replace with custom input network
working_dir = "./outputs/working_dir"  # user to specify where to put intermediate stage output files
final_clustering = "./outputs/final_clustering.csv"

os.makedirs(working_dir, exist_ok=True)

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
        aoc
        TO BE EXPANDED
"""

# example pipeline
method_arr = {
    # "ikc": {
    #     "k": 2,
    # },
    "infomap": {},
    # "leiden-cpm": {
    #     "res": 0.1,
    # },
    # "aoc": {
    #     "m": "k2",
    # },
    "wcc": {
        "threshold": "1log10",  # c, xlog_y(n)
    },
}
run_pipeline(input_network, working_dir, final_clustering, method_arr)
