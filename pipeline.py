import os

modules_location = "./modules"
external_modules_location = "./downloaded_programs"

def run_pipeline(input_network, working_dir, final_clustering, method_arr):
    """This is a generic method that takes in an input network and runs all the methods in method_arr
    The output of the previous stage networks and clusterings get fed to the next stages input
    """
    previous_stage_network = input_network
    previous_stage_clustering = None
    for stage_number, method in enumerate(method_arr):
        previous_stage_network, previous_stage_clustering = run_method(
            method=method,
            method_params=method_arr[method],
            current_network=previous_stage_network,
            current_clustering=previous_stage_clustering,
            working_dir=working_dir,
            stage_number=stage_number,
        )

    os.system(f"mv {previous_stage_clustering} {final_clustering}")


def run_method(
    method,
    method_params,
    current_network,
    current_clustering,
    working_dir,
    stage_number,
):
    """This method showcases different example commands for different programs."""
    match method:
        case "leiden-mod":
            leiden_location = f"{modules_location}/run_leiden.py"
            leiden_output = f"{working_dir}/{stage_number}_{method}.csv"
            os.system(
                f"python {leiden_location} --edgelist {current_network} --output {leiden_output} --model mod"
            )
            return current_network, leiden_output

        case "leiden-cpm":
            leiden_location = f"{modules_location}/run_leiden.py"
            leiden_output = f"{working_dir}/{stage_number}_{method}.csv"
            os.system(
                f"python {leiden_location} --edgelist {current_network} --output {leiden_output} --model cpm --resolution {method_params['res']}"
            )
            return current_network, leiden_output

        case "ikc":
            ikc_location = f"{modules_location}/run_ikc.py"
            ikc_output = f"{working_dir}/{stage_number}_{method}.csv"
            command = f"python {ikc_location} --edgelist {current_network} --output {ikc_output}"

            # Argument
            if "k" in method_params: command = f"{command} -k {method_params["k"]}"
            os.system(command)
            return current_network, ikc_output

        case "infomap":
            infomap_location = f"{modules_location}/run_infomap.py"
            infomap_output = f"{working_dir}/{stage_number}_{method}.csv"
            os.system(
                f"python {infomap_location} --edgelist {current_network} --output-directory {infomap_output}"
            )
            return current_network, infomap_output

        case "wcc":
            wcc_location = f"{external_modules_location}/constrained_clustering"
            wcc_output = f"{working_dir}/{stage_number}_{method}.csv"
            os.system(
                f"{wcc_location} MincutOnly --edgelist {current_network} --existing-clustering {current_clustering} --output-file {working_dir}/{stage_number}.csv --num-processors 1 --log-file {working_dir}/{stage_number}.log --connectedness-criterion 1 --log-level 1"
            )
            return current_network, wcc_output

        case "cc":
            cc_location = f"{external_modules_location}/constrained_clustering"
            cc_output = f"{working_dir}/{stage_number}_{method}.csv"
            os.system(
                f"{cc_location} MincutOnly --edgelist {current_network} --existing-clustering {current_clustering} --output-file {working_dir}/{stage_number}.csv --num-processors 1 --log-file {working_dir}/{stage_number}.log --connectedness-criterion 0 --log-level 1"
            )
            return current_network, cc_output

        # TODO: AOC should only be called when there is IKC in the previous stage
        case "aoc":
            aoc_location = f"{external_modules_location}/aoc"
            pass


""" Step 1: specify input network, working directory, and final output clustering name"""
input_network = "./inputs/network.csv"  # user to replace with custom input network
working_dir = "./output/working_dir"  # user to specify where to put intermediate stage output files
final_clustering = "./output/final_clustering.csv"

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
        TO BE EXPANDED
"""

# live demo should swap oout leiden-cpm with leiden-mod, swap out cc with wcc, and so on
method_arr = {
    "ikc": {
        "k": 10,
    },
    "cm": {
        "clustering": "leiden",
        "threshold": "1log10",
    },
    "wcc": {
        "threshold": "1log10",  # c, xlog_y(n)
    },
}
run_pipeline(input_network, working_dir, final_clustering, method_arr)
