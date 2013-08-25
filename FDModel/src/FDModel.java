/**
 * Created with IntelliJ IDEA.
 * User: eugeneai
 * Date: 23.08.13
 * Time: 22:41
 * To change this template use File | Settings | File Templates.
 */
public class FDModel {
    public FDNode node;
    public FDModel (FDNode aNode) {
        this.node=aNode;
    }
    public FDModel () {
        this.node=new FDNode(0.0);
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
}
