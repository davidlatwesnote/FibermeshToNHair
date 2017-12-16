import maya.OpenMaya as om
import maya.cmds as cmds


# takes a curve and mesh dag path and calculates the closest UV point from the first cv on that curve
def getUVatCV(curveName, meshName):
    sel = om.MSelectionList()

    sel.add(curveName)
    sel.add(meshName)

    curveDag = om.MDagPath()
    meshDag = om.MDagPath()

    sel.getDagPath(0, curveDag)
    sel.getDagPath(1, meshDag)

    fnMesh = om.MFnMesh(meshDag)
    fnCurve = om.MFnNurbsCurve(curveDag)

    # first get the location of the first cv in our curve
    cvPoint = om.MPoint()
    fnCurve.getCV(0, cvPoint, om.MSpace.kWorld)

    # get the closest point on the mesh from that cv point
    closestPoint = om.MPoint()
    fnMesh.getClosestPoint(cvPoint, closestPoint, om.MSpace.kWorld)

    # get the uv at that point
    # create a MScriptUtil object because python doesn't have a double float type
    util = om.MScriptUtil()
    util.createFromList([0.0, 0.0], 2)
    uvPoint = util.asFloat2Ptr()

    fnMesh.getUVAtPoint(closestPoint, uvPoint, om.MSpace.kWorld)
    u = om.MScriptUtil.getFloat2ArrayItem(uvPoint, 0, 0)
    v = om.MScriptUtil.getFloat2ArrayItem(uvPoint, 0, 1)

    return [u, v]


def setupHairSystemFromCurves(follicleGroup, meshName):
    follicles = cmds.listRelatives(follicleGroup)

    for f in follicles:
        rel = cmds.listRelatives(f)
        follicleShape = rel[0]
        curve = rel[1]
        meshShape = cmds.pickWalk(meshName, d="down")[0]

        # first unparent our curve from the mesh
        cmds.parent(curve, w=1)

        # connect the outMesh of our mesh's shape to the inputMesh of our follicle shape
        cmds.connectAttr(meshShape + ".outMesh", follicleShape + ".inputMesh")

        # connect the worldMatrix[0] to our follicle shape's inputWorldMatrix
        cmds.connectAttr(meshShape + ".worldMatrix[0]", follicleShape + ".inputWorldMatrix")

        # connect outTranslate and outRotate of our follicle shape to our follicle's transform
        cmds.connectAttr(follicleShape + ".outTranslate", f + ".t")
        cmds.connectAttr(follicleShape + ".outRotate", f + ".r")

        # calculate the uv at that follicle
        uv = getUVatCV(curveName=curve, meshName=meshName)

        # set our UV values on our follicleShape to that
        cmds.setAttr(follicleShape + ".parameterU", uv[0])
        cmds.setAttr(follicleShape + ".parameterV", uv[1])

        # reparent our curve
        cmds.parent(curve, f)
