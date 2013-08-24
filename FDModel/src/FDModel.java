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
    public double euler(double dt) {
        // Integrate graph in two steps
    }
}
