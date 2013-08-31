package org.icc.fd;

import sun.org.mozilla.javascript.Context;
import sun.org.mozilla.javascript.Scriptable;
import sun.org.mozilla.javascript.ScriptableObject;

import org.icc.fd.*;

/**
 * Created with IntelliJ IDEA.
 * User: eugeneai
 * Date: 30.08.13
 * Time: 14:23
 * To change this template use File | Settings | File Templates.
 */
public class Scripting {
    public Context context;
    public Scriptable scope;

    Scripting () {
        this.context = Context.enter();
        this.scope = this.context.initStandardObjects();
        //this.scope.put("a42", null, 42);
        try {
            ScriptableObject.defineClass(scope, JSMyCounter.class);
        }
        catch (Throwable e) {
            System.err.println("JS init exception: "+e);
        }
        // Create one instance of Counter/JSMyCounter
        Object[] arg = { new Integer(7) };
        Scriptable myCounter = this.context.newObject(scope, "Counter", arg);
        scope.put("myCounter", scope, myCounter);

        //ScriptableObject.defineClass(scope, FDArc);
        //ScriptableObject.defineClass(scope, FDNode);
        //TODO load our context objects as, e.g., a global variale FD, or fd;
    }

    @Override
    protected void finalize() throws Throwable {
        this.context.exit();
        super.finalize();
    }

    public Object evaluateString(String cmd, boolean logging) {
        Object rc = this.context.evaluateString(this.scope, cmd, "<FDModel.JS.context.cmd>", 1, null);
        if (logging) {
            System.out.print(Context.toString(rc));
        }
        return rc;
    }

    public Object evaluateString(String cmd) {
        return this.evaluateString(cmd, false);
    }

    public static void main (String [] args) {
        System.out.println("Javascript test.");
        Scripting js=new Scripting();
        Object rc = js.evaluateString("myCounter.count+1;");
        System.out.print("Result:");
        System.out.println(rc);
        rc = js.evaluateString("myCounter.count+1;");
        System.out.print("Result:");
        System.out.println(rc);
    }
}
