from kipy import KiCad

if __name__ == "__main__":
    kicad = KiCad()
    net_classes = kicad.get_project(kicad.get_board().document).get_net_classes()
    class_names = [t.name for t in net_classes]
    print(f"class_names: {class_names}")
    for name in class_names:
        print(f"class_name: {name}")
        nets = kicad.get_board().get_nets(netclass_filter=name)
        print(f"{name} nets: {nets}")

    nets = kicad.get_board().get_nets()
    result_dict = kicad.get_board().get_netclass_for_nets(nets)
    for net_name, net_class_obj in result_dict.items():
        print(f"Net Name: {net_name}")
        print(f"  -> NetClass: {net_class_obj.name}")
        print(f"  -> Priority: {net_class_obj.priority}")
        print("-" * 40)
    