//package com.sandeep.rhino.js;

import org.mozilla.javascript.Context;
import org.mozilla.javascript.Script;
import org.mozilla.javascript.Scriptable;

public class RhinoJavaScriptDemo {


    public static void main(String[] args) {

        Context mozillaJsContext = Context.enter();
        Scriptable scope = mozillaJsContext.initStandardObjects();

    /*A Javascript JSON Object*/
        String source = "{a :{5+6}}";
        Script scriptjs = mozillaJsContext.compileString(source, "sandeepDemoScript", 1, null);

    /*Result is a Javascript Object*/
        Object jsObjectResult = scriptjs.exec(mozillaJsContext, scope);
        String result = Context.toString(jsObjectResult);
        System.out.println("After Evaluating JS Object value is: "+result);
    }

}
