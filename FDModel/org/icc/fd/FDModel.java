package org.icc.fd;

import java.util.ArrayList;

/**
 * Created with IntelliJ IDEA.
 * User: eugeneai
 * Date: 23.08.13
 * Time: 22:41
 * To change this template use File | Settings | File Templates.
 */

public class FDModel {
    public FDNode node;
    protected int yearsToModel;

    public static interface Action {
        public void execute(FDNode node);
    }

    public static interface DTAction {
        public void execute(FDNode node, double dt);
    }

    // Some popular actions
    public static class EraseAction implements Action {
        public void execute(FDNode node) {
            node.dVal = 0.0;
        }
    }
    public static class AddAction extends EraseAction implements Action {
        public void execute(FDNode node) {
            node.val+=node.dVal;
            super.execute(node);
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
            this.nodeExecute(node, ea); // dt ignored here
        }

        protected void addIncrement(FDNode node) {
            AddAction a = new AddAction();
            this.nodeExecute(node, a); // dt also ignored
        }
        public void nodeExecute(FDNode node, DTAction action, double dt) {
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
        public void nodeExecute(FDNode node, Action action) {
            FDNode currNode;
            FDArc currArc;
            if (node == null) return;
            if (node.marked) return;
            node.marked = true;
            currNode = node;
            action.execute(node);
            currArc = currNode.siblings;
            while (currArc != null) {
                this.nodeExecute(currArc.target, action);
                currArc = currArc.next;
            }
            node.marked = false;
        }

    }

    public ArrayList<Action> actions;

    public FDModel (FDNode aNode) {
        this.node=aNode;
        this.yearsToModel = 0;
        this.actions=new ArrayList<Action>();
    }

    public FDModel () {
        this(new FDNode(0.0));
    }

    public void addAction(Action ac) {
        this.actions.add(ac);
    }

    protected void fireActions(FDNode node, double dt) {
        for (Action ac: actions) {
            ac.execute(node);
        }
    }

    public void step(IntegrationTechnique t, double dt) {
        t.step(this.node, dt);
    }

    public int simulate(IntegrationTechnique t, int yearsToModel, int steps) {
        this.yearsToModel=yearsToModel;
        double dt = 1.0/steps;
        this.fireActions(this.node, dt);
        for (int year = 1; year <= yearsToModel; year ++) {
            for (int step = 0; step<steps; step++) {
                this.step(t, dt);
            };
            this.fireActions(this.node, dt);
        }
        return yearsToModel;
    }
}

