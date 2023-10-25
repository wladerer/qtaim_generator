import json
import os
import numpy as np


def parse_cp(lines, verbose=True):
    """
    Takes
        lines: list of lines from cp file
    Returns
        cp_dict: dictionary of critical point information
    """
    lines_split = [line.split() for line in lines]
    cp_bond, cp_atom = False, False
    cp_name = "null"
    cp_dict = {}
    if "(3,-3)" in lines_split[0]:
        cp_atom = True
        if verbose:
            print("atom cp")

    elif "(3,-1)" in lines_split[0]:
        cp_bond = True
        if verbose:
            print("bond cp")

    else:
        if verbose:
            print("ring critical bond not implemented")
        return "ring", cp_dict

    cp_atom_conditionals = {
        "cp_num": ["----------------"],
        "ele_info": ["Corresponding", "nucleus:"],
        "pos_ang": ["Position", "(Angstrom):"],
        "Lagrangian_K": ["Lagrangian", "kinetic", "energy"],
        "Hamiltonian_K": ["Hamiltonian", "kinetic", "energy"],
        "e_density": ["Energy", "density", "E(r)"],
        "lap_e_density": ["Laplacian", "electron", "density:"],
        "e_loc_func": ["Electron", "localization", "function"],
        "ave_loc_ion_E": ["Average", "local", "ionization", "energy"],
        "delta_g_promolecular": ["Delta-g", "promolecular"],
        "delta_g_hirsh": ["Delta-g", "Hirshfeld"],
        "esp_nuc": ["ESP", "nuclear", "charges:"],
        "esp_e": ["ESP", "electrons:"],
        "esp_total": ["Total", "ESP:"],
        "grad_norm": ["Components", "gradient", "x/y/z"],
        "lap_norm": ["Components", "Laplacian", "x/y/z"],
        "eig_hess": ["Eigenvalues", "Hessian:"],
        "det_hessian": ["Determinant", "Hessian:"],
        "ellip_e_dens": ["Ellipticity", "electron", "density:"],
        "eta": ["eta", "index:"],
    }

    cp_bond_conditionals = {
        "cp_num": ["----------------"],
        "connected_bond_paths": ["Connected", "atoms:"],
        "pos_ang": ["Position", "(Angstrom):"],
        "Lagrangian_K": ["Lagrangian", "kinetic", "energy"],
        "Hamiltonian_K": ["Hamiltonian", "kinetic", "energy"],
        "e_density": ["Energy", "density", "E(r)"],
        "lap_e_density": ["Laplacian", "electron", "density:"],
        "e_loc_func": ["Electron", "localization", "function"],
        "ave_loc_ion_E": ["Average", "local", "ionization", "energy"],
        "delta_g_promolecular": ["Delta-g", "promolecular"],
        "delta_g_hirsh": ["Delta-g", "Hirshfeld"],
        "esp_nuc": ["ESP", "nuclear", "charges:"],
        "esp_e": ["ESP", "electrons:"],
        "esp_total": ["Total", "ESP:"],
        "grad_norm": ["Components", "gradient", "x/y/z"],
        "lap_norm": ["Components", "Laplacian", "x/y/z"],
        "eig_hess": ["Eigenvalues", "Hessian:"],
        "det_hessian": ["Determinant", "Hessian:"],
        "ellip_e_dens": ["Ellipticity", "electron", "density:"],
        "eta": ["eta", "index:"],
    }

    if cp_atom:
        unknown_id = 0
        for ind, i in enumerate(lines_split):
            for k, v in cp_atom_conditionals.items():
                if all(x in i for x in v):
                    if k == "cp_num":
                        cp_dict[k] = int(i[2][:-1])

                    elif k == "pos_ang":
                        cp_dict[k] = [float(x) for x in i[2:]]

                    elif k == "ele_info":
                        if i[2] == "Unknown":
                            cp_name = str(unknown_id) + "_Unknown"
                            cp_dict["number"] = "Unknown"
                            cp_dict["ele"] = "Unknown"
                            unknown_id += 1
                        else:
                            cp_dict["element"] = i[2].split("(")[1]
                            cp_dict["number"] = i[2].split("(")[0]
                            cp_name = cp_dict["number"] + "_" + cp_dict["element"]

                    elif k == "esp_total":
                        cp_dict[k] = float(i[2])

                    elif k == "eig_hess":
                        cp_dict[k] = np.sum(np.array([float(x) for x in i[-3:]]))

                    elif k == "grad_norm" or k == "lap_norm":
                        cp_dict[k] = float(lines_split[ind + 2][-1])

                    else:
                        # print(i)
                        cp_dict[k] = float(i[-1])

                    cp_atom_conditionals.pop(k)
                    break

    elif cp_bond:
        for ind, i in enumerate(lines_split):
            for k, v in cp_bond_conditionals.items():
                if all(x in i for x in v):
                    if k == "cp_num":
                        cp_dict[k] = int(i[2][:-1])
                        cp_name = str(cp_dict[k]) + "_bond"
                    elif k == "connected_bond_paths":
                        list_raw = [x for x in i[2:]]
                        list_raw = [list_raw[0], list_raw[-2]]
                        list_raw = [int(x.split("(")[0]) for x in list_raw]
                        cp_dict[k] = list_raw
                    elif k == "pos_ang":
                        cp_dict[k] = [float(x) for x in i[2:]]
                    elif k == "esp_total":
                        cp_dict[k] = float(i[2])
                    elif k == "eig_hess":
                        cp_dict[k] = np.sum(np.array([float(x) for x in i[-3:]]))
                    elif k == "grad_norm" or k == "lap_norm":
                        cp_dict[k] = float(lines_split[ind + 2][-1])

                    else:
                        cp_dict[k] = float(i[-1])
                    # print(v)
                    cp_bond_conditionals.pop(k)

                    break

    else:
        print("error")

    return cp_name, cp_dict


def get_qtaim_descs(file="./CPprop_1157_1118_1158.txt", verbose=False):
    """
    helper function to parse CPprop file from multiwfn.
    Takes
        file (str): path to CPprop file
        verbose(bool): prints dictionary of descriptors
    returns: dictionary of descriptors
    """
    cp_dict, ret_dict = {}, {}

    with open(file) as f:
        lines = f.readlines()
        lines = [line[:-1] for line in lines]

    # section lines into segments on ----------------
    track = 0
    for ind, line in enumerate(lines):
        if "----------------" in line:
            lines_segment = []
        lines_segment.append(line)
        if ind < len(lines) - 1:
            if "----------------" in lines[ind + 1]:
                cp_dict[track] = lines_segment
                track += 1
        else:
            cp_dict[track] = lines_segment

    for k, v in cp_dict.items():
        ind_atom, cp_dict = parse_cp(v, verbose=verbose)
        ret_dict[ind_atom] = cp_dict

    # remove keys-value pairs that are "ring"
    ret_dict = {k: v for k, v in ret_dict.items() if "ring" not in k}
    return ret_dict


def dft_inp_to_dict(dft_inp_file):
    """
    helper function to parse dft input file.
    Takes
        dft_inp_file (str): path to dft input file
    returns: dictionary of atom positions
    """
    atom_dict = {}

    with open(dft_inp_file) as f:
        lines = f.readlines()
        # strip tabs
        lines = [line[:-1] for line in lines]

    # find line starting with "* xyz"
    for ind, line in enumerate(lines):
        if "* xyz" in line:
            xyz_ind = ind
            break

    # filter lines before and including xyz_ind
    lines = lines[xyz_ind + 1 : -1]

    for ind, line in enumerate(lines):
        line_split = line.split()
        atom_dict[ind] = {
            "element": line_split[0],
            "pos": [float(x) for x in line_split[1:]],
        }

    return atom_dict


def only_atom_cps(qtaim_descs):
    """
    separates qtaim descriptors into atom and bond descriptors
    """
    ret_dict = {}
    ret_dict_bonds = {}
    for k, v in qtaim_descs.items():
        if "bond" not in k and "Unknown" not in k:
            ret_dict[k] = v
        if "bond" in k:
            ret_dict_bonds[k] = v
    return ret_dict, ret_dict_bonds


def find_cp(atom_dict, atom_cp_dict, margin=0.5):
    """
    From a dictionary of atom ind, position, and element, find the corresponding cp in the atom_cp_dict
    Takes:
        atom_dict: dict
            dictionary of atom ind, position, and element
        atom_cp_dict: dict
            dictionary of cp ind, position, and element
    Returns:
        cp_key: str
            key of cp_dict
        cp_dict: dict
            dictionary of cp values matching atom
    """

    for k, v in atom_cp_dict.items():
        element_cond = v["element"] == atom_dict["element"]
        # print(v["element"], atom_dict["element"])
        if element_cond:
            distance = np.linalg.norm(
                np.array(v["pos_ang"]) - np.array(atom_dict["pos"])
            )
            dist_cond = distance < margin
            if dist_cond:
                return k, v

    return False, {}


def find_cp_map(dft_dict, atom_cp_dict, margin=0.5):
    """
    Iterate through dft dict and find nearest cp in atom_cp_dict
    Takes:
        dft_dict: dict
            dictionary of dft atoms
        atom_cp_dict: dict
            dictionary of qtaim atoms
    Returns:
        ret_dict (dict): dictionary with dft atoms as keys and cp_dict as values
        qtaim_to_dft (dict): dictionary with qtaim atoms as keys and dft atoms as values
        missing_atoms (list): list of dft atoms that do not have a cp found in qtaim
    """
    ret_dict, qtaim_to_dft = {}, {}
    missing_atoms = []
    for k, v in dft_dict.items():
        v_send = {"element": v["element"], "pos": v["pos"], "ind": k}

        ret_key, dict_ret = find_cp(
            v_send, atom_cp_dict, margin=margin
        )  # find_cp returns cp_key, cp_dict

        if ret_key != False:
            ret_dict[k] = dict_ret
            qtaim_to_dft[k] = {"key": ret_key, "pos": dict_ret["pos_ang"]}
        else:
            # print("CP no match found in dft")
            ret_dict[k] = {}
            qtaim_to_dft[k] = {"key": -1, "pos": []}
            missing_atoms.append(k)

    return ret_dict, qtaim_to_dft, missing_atoms


def find_bond_cp(i, bonds_cps):
    """
    Takes:
        i: list
            list of two atom indices
        bonds_cps: dict
            dictionary of bond cps
    Returns:
        dict_cp_bond: dict
            dictionary of cp values for bond
    """
    for k, v in bonds_cps.items():
        if i == v["atom_inds"] or i == [v["atom_inds"][1], v["atom_inds"][0]]:
            return v

    return False


def add_closest_atoms_to_bond(bond_cps, dft_dict, margin=1.0):
    """
    Takes in bonds cps and adds the index of the closest atoms to the bond
    Takes:
        bond_cps: dict
            dictionary of bond cps
        dft_to_qtaim: dict
            dictionary of dft to qtaim atom indices
    Returns:
        bond_cps: dict
            dictionary of bond cps with closest atoms added
    """
    for k, v in bond_cps.items():
        for i in k:
            dists = []
            for j in dft_dict.keys():
                dists.append(
                    np.linalg.norm(
                        np.array(v["pos_ang"]) - np.array(dft_dict[j]["pos"])
                    )
                )
            # yell if the two closest atoms are further than margin
            if np.sort(dists)[:2].tolist()[1] > margin:
                print("Warning: bond cp is far from bond")
            bond_cps[k]["atom_inds"] = np.argsort(dists)[:2].tolist()
    return bond_cps


def bond_cp_distance(bond_cps, bond_list, dft_dict, margin=2.0):
    """
    Takes in bond cps and finds the closest atoms to the bond
    Takes:
        bond_cps (dict): dictionary of bond cps
        bond_list (list): list of bonds
        bond_defn (str): bond definition, either "distance" or "qtaim"
        dft_dict (dict): dictionary of dft atoms
    Returns:
        ret_dict (dict): dictionary of bond cps with closest atoms added
    """

    ret_dict = {}

    bond_cps = add_closest_atoms_to_bond(
        bond_cps, dft_dict, margin=margin
    )  # gets atoms from bond cps

    for i in bond_list:
        dict_cp_bond = find_bond_cp(
            i, bond_cps
        )  # gets bond cp dictionary from bond_cps
        if dict_cp_bond != False:  # remaps to [atom1, atom2] : qtaim_dict
            ret_dict[tuple(i)] = dict_cp_bond
        else:
            # print("No bond found for ", i)
            ret_dict[tuple(i)] = {}

    return ret_dict


def merge_qtaim_inds(
    qtaim_descs, dft_inp_file, bond_list=None, define_bonds="qtaim", margin=2.0
):
    """
    Gets mapping of qtaim indices to atom indices and remaps atom CP descriptors

    Takes
        qtaim_descs: dict of qtaim descriptors
        dft_inp_file: str input file for dft
    returns:
        dict of qtaim descriptors ordered by atoms in dft_inp_file
    """

    # open dft input file
    dft_dict = dft_inp_to_dict(dft_inp_file)
    # find only atom cps to map
    atom_only_cps, bond_cps = only_atom_cps(qtaim_descs)
    # remap qtaim indices to atom indices
    atom_cps_remapped, qtaim_to_dft, missing_atoms = find_cp_map(
        dft_dict, atom_only_cps, margin=0.5
    )
    # remapping bonds
    bond_list_ret = []
    if define_bonds == "qtaim":
        bond_cps_qtaim = {}
        bond_cps = {
            k: v for k, v in bond_cps.items() if "connected_bond_paths" in v.keys()
        }
        for k, v in bond_cps.items():
            bond_list_unsorted = v["connected_bond_paths"]
            bond_list_unsorted = [
                int(qtaim_to_dft[i - 1]["key"].split("_")[0]) - 1
                for i in bond_list_unsorted
            ]
            bond_list_unsorted = sorted(bond_list_unsorted)
            bond_cps_qtaim[tuple(bond_list_unsorted)] = v
            bond_list_ret.append(bond_list_unsorted)
        bond_cps = bond_cps_qtaim

    else:
        bond_cps = bond_cp_distance(bond_cps, bond_list, dft_dict, margin=margin)
    # merge dictionaries
    ret_dict = {**atom_cps_remapped, **bond_cps}
    return ret_dict


def gather_imputation(
    df,
    features_atom,
    features_bond,
    root_dir="../data/hydro/",
    json_file_imputed="./imputed_vals.json",
    reaction=False,
    define_bonds="qtaim",
):
    """
    Takes in dataframe and features and returns dictionary of imputation values
    Takes:
        df (pandas dataframe): dataframe of data
        features_atom (list): list of atom features
        features_bond (list): list of bond features
        root_dir (str): root directory of data
        json_file_imputed (str): json file to store imputation values
        define_bonds (str): bond definition, either "distance" or "qtaim"
    Returns:
        impute_dict (dict): dictionary of imputation values
    """

    impute_dict = {"atom": {}, "bond": {}}
    for i in features_atom:
        impute_dict["atom"][i] = []
    for i in features_bond:
        impute_dict["bond"][i] = []

    if os.path.exists(json_file_imputed):
        print("attempting to use previously stored imputation values")
        with open(json_file_imputed, "r") as f:
            impute_dict = json.load(f)
        return impute_dict

    else:
        for ind, row in df.iterrows():
            if reaction:
                try:
                    reaction_id = row["reaction_id"]
                    if define_bonds == "distances":
                        bonds_reactants = row["reactant_bonds"]
                    QTAIM_loc_reactant = (
                        root_dir + "QTAIM/" + str(reaction_id) + "/reactants/"
                    )
                    cp_file_reactants = QTAIM_loc_reactant + "CPprop.txt"
                    dft_inp_file_reactant = QTAIM_loc_reactant + "input.in"

                    qtaim_descs_reactants = get_qtaim_descs(
                        cp_file_reactants, verbose=False
                    )
                    if define_bonds == "distances":
                        bonds_products = row["product_bonds"]

                    QTAIM_loc_product = (
                        root_dir + "QTAIM/" + str(reaction_id) + "/products/"
                    )
                    cp_file_products = QTAIM_loc_product + "CPprop.txt"
                    dft_inp_file_product = QTAIM_loc_product + "input.in"
                    qtaim_descs_products = get_qtaim_descs(
                        cp_file_products, verbose=False
                    )

                    mapped_descs_reactants = merge_qtaim_inds(
                        qtaim_descs_reactants,
                        bonds_reactants,
                        dft_inp_file_reactant,
                        define_bonds=define_bonds,
                    )

                    mapped_descs_products = merge_qtaim_inds(
                        qtaim_descs_products,
                        bonds_products,
                        dft_inp_file_product,
                        define_bonds=define_bonds,
                    )

                    for k, v in mapped_descs_reactants.items():
                        if v == {}:
                            pass
                        elif type(k) == tuple:
                            for i in features_bond:
                                impute_dict["bond"][i].append(v[i])
                        elif type(k) == int:
                            for i in features_atom:
                                impute_dict["atom"][i].append(v[i])
                        else:
                            pass

                    for k, v in mapped_descs_products.items():
                        if v == {}:
                            pass
                        elif type(k) == tuple:
                            for i in features_bond:
                                impute_dict["bond"][i].append(v[i])
                        elif type(k) == int:
                            for i in features_atom:
                                impute_dict["atom"][i].append(v[i])
                        else:
                            pass

                except:
                    print(reaction_id)
            else:  # for single molecules
                try:
                    bonds = []
                    id = row["ids"]
                    if define_bonds == "distances":
                        bonds = row["bonds"]
                    # bonds = row["bonds"]
                    QTAIM_loc = root_dir + "QTAIM/" + str(id) + "/"
                    cp_file = QTAIM_loc + "CPprop.txt"
                    dft_inp_file = QTAIM_loc + "input.in"

                    qtaim_descs = get_qtaim_descs(cp_file, verbose=False)
                    mapped_descs = merge_qtaim_inds(
                        qtaim_descs, bonds, dft_inp_file, define_bonds=define_bonds
                    )
                    for k, v in mapped_descs.items():
                        if v == {}:
                            pass
                        elif type(k) == tuple:
                            for i in features_bond:
                                impute_dict["bond"][i].append(v[i])
                        elif type(k) == int:
                            for i in features_atom:
                                impute_dict["atom"][i].append(v[i])
                        else:
                            pass

                except:
                    print("error, id: ", id)

    # get the mean and median of each feature
    for k, v in impute_dict.items():
        for k1, v1 in v.items():
            impute_dict[k][k1] = {
                "mean": np.mean(np.array(v1)),
                "median": np.median(np.array(v1)),
            }
    # save dictionary as json
    with open(json_file_imputed, "w") as f:
        json.dump(impute_dict, f)

    return impute_dict
