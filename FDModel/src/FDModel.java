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
    // Integrate graph in three steps
    public void clearNewVals(FDNode node) {
        FDNode currNode, nextNode;
        FDArc currArc;
        if (node == null) return;
        // The first step. Erasing newVals of all the graph nodes.
        currNode = node;
        currArc = currNode.siblings;
        currNode.newVal = 0.0;
        while (currArc != null) {
            this.clearNewVals(currArc.target);
            currArc = currArc.next;
        }
    }
}
