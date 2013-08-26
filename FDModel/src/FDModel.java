import java.util.HashMap;
import java.util.ArrayList;
import org.jfree.data.xy.XYSeries;

/**
 * Created with IntelliJ IDEA.
 * User: eugeneai
 * Date: 23.08.13
 * Time: 22:41
 * To change this template use File | Settings | File Templates.
 */
public class FDModel {
    protected static class FDSymbol {
        FDNode node;
        XYSeries list;
        public FDSymbol(FDNode node, int maxSize, String name) {
            this.node = node;
            list = new XYSeries(name, false);
        }
    }
    public FDNode node;
    public HashMap<String, FDSymbol> symbolTable;
    public HashMap<FDNode, String> nodeTable;
    // public int maxModellingPeriod;
    protected int yearsToModel;

    public FDModel (FDNode aNode) {
        this.node=aNode;
        this.symbolTable = new HashMap<String, FDSymbol>(100);
        this.nodeTable = new HashMap<FDNode, String>(100);
        this.yearsToModel = 0;
    }
    public FDModel () {
        this(new FDNode(0.0));
    }

    public static interface Action {
        public void execute(FDNode node, double dt);
    }

    // Some popular actions
    public static class EraseAction implements Action {
        public void execute(FDNode node, double dt) {
            node.dVal = 0.0;
        }
    }
    public static class AddAction extends EraseAction implements Action {
        public void execute(FDNode node, double dt) {
            node.val+=node.dVal;
            super.execute(node, dt);
        }
    }

    public static interface IntegrationTechnique {
        public void step(FDNode root, double dt);
        public void integrationStep(FDNode root, double dt);
    }

    public static class BaseIntegrationTechnique implements IntegrationTechnique {
        // Implement some basic functionality
        public void step(FDNode root, double dt) {
            // Do nothing here except cleaning;
            this.clearNewVals(root);
            this.integrationStep(root, dt);
            this.addIncrement(root);
        }
        public void integrationStep(FDNode node, double dt) {
            // Do nothing.
        }
        protected void clearNewVals(FDNode node) {
            EraseAction ea = new EraseAction();
            this.nodeExecute(node, ea, 0.0); // dt ignored here
        }

        protected void addIncrement(FDNode node) {
            AddAction a = new AddAction();
            this.nodeExecute(node, a, 0.0); // dt also ignored
        }
        public void nodeExecute(FDNode node, Action action, double dt) {
            FDNode currNode;
            FDArc currArc;
            if (node == null) return;
            if (node.marked) return;
            node.marked = true;
            currNode = node;
            action.execute(node, dt);
            currArc = currNode.siblings;
            while (currArc != null) {
                this.nodeExecute(currArc.target, action, dt);
                currArc = currArc.next;
            }
            node.marked = false;
        }

    }

    public void step(IntegrationTechnique t, double dt) {
        t.step(this.node, dt);
    }

    public FDNode define(FDNode node, String name) {
        this.symbolTable.put(name, new FDSymbol(node, this.yearsToModel, name));
        this.nodeTable.put(node, name);
        return node;
    }
    public FDNode getNode(String name) {
        return ((FDSymbol) this.symbolTable.get(name)).node;
    }
    public XYSeries getSeries(String name) {
        return ((FDSymbol) this.symbolTable.get(name)).list;
    }
    public XYSeries getSeries(FDNode node) {
        return this.getSeries((String) this.nodeTable.get(node));
    }
    public double storeAs(double val, String name) {
        XYSeries s = this.symbolTable.get(name).list;
        s.add(s.getItemCount() + 1, val);
        return val;
    }
    public double get(String name, int index) {
        return this.symbolTable.get(name).list.getY(index).doubleValue();
    }

    public int simulate(IntegrationTechnique t, int yearsToModel, int steps) {
        this.yearsToModel=yearsToModel;
        double dt = 1.0/steps;
        this.storeSeries();
        for (int year = 1; year <= yearsToModel; year ++) {
            for (int step = 0; step<steps; step++) {
                this.step(t, dt);
            };
            this.storeSeries();
        }
        return yearsToModel;
    }

    protected void storeSeries() {
        for (FDSymbol s: this.symbolTable.values()) {
            this.storeAs(s.node.val, (String) s.list.getKey());
        }
    }
}
