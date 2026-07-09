import com.comsol.model.*;
import com.comsol.model.util.*;

public class ComsolCube10mm {
  public static Model run() {
    Model model = ModelUtil.create("Model");
    model.modelNode().create("mod1");
    model.label("ComsolCube10mm.mph");
    model.param().set("L", "10[mm]", "Smoke-test cube side length");

    model.component().create("comp1", true);
    model.component("comp1").geom().create("geom1", 3);
    model.component("comp1").geom("geom1").lengthUnit("mm");
    model.component("comp1").geom("geom1").create("blk1", "Block");
    model.component("comp1").geom("geom1").feature("blk1").set("size", new String[]{"L", "L", "L"});
    model.component("comp1").geom("geom1").feature("blk1").set("base", "center");
    model.component("comp1").geom("geom1").run();

    model.component("comp1").material().create("mat1", "Common");
    model.component("comp1").material("mat1").label("Generic steel smoke material");
    model.component("comp1").material("mat1").propertyGroup("def").set("density", "7850[kg/m^3]");
    model.component("comp1").material("mat1").propertyGroup("def").set("thermalconductivity", "45[W/(m*K)]");
    model.component("comp1").material("mat1").propertyGroup("def").set("heatcapacity", "470[J/(kg*K)]");

    model.component("comp1").mesh().create("mesh1");
    model.component("comp1").mesh("mesh1").autoMeshSize(4);
    model.component("comp1").mesh("mesh1").run();
    return model;
  }

  public static void main(String[] args) {
    Model model = run();
    String out = args.length > 0 ? args[0] : "../outputs/comsol_cube_10mm.mph";
    model.save(out);
  }
}
