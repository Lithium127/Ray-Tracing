from rtrace import Camera, Scene, Point3, SkyBox, Color, Assets, Mat


""" =========== """
"""  CONSTANTS  """
""" =========== """

# Image Information
RENDER_IMG_WIDTH    = 1024
RENDER_ASPECT_RATIO = 16/9
SAVE_PATH = "images"
FILE_NAME = "test"

# Rendering Quality
SAMPLES_PER_PIXEL = 16
RAY_BOUNCE_LIMIT  = 64

# Camera Data
CAMERA_CENTER  = Point3(0, 0, 1.5)
CAMERA_LOOK_AT = Point3(0, 0, -1)
FIELD_OF_VIEW  = 60
DRAW_SILENT    = True
MULTIPROCESS   = True




def main():
    scene = Scene(
        [
            # Ground object
            Assets.Sphere(
                Point3(0, -100.5, -1), 
                100, 
                Mat.Lambertian(Color.GRAY()),
            ),
            Assets.Sphere(
                Point3(1, 0, -1.75),
                0.5,
                Mat.Dielectric.Glass()
            ),
            Assets.Sphere(
                Point3(0, 0, -1),
                0.5,
                Mat.VectorShade()
            ),
            Assets.Sphere(
                Point3(-1.2, 0, -1),
                0.5,
                Mat.Metal(Color.GRAY())
            ),
        ],
        skybox = SkyBox.Lerp(
            Color(0.7, 0.5, 1),
            Color(0.9, 0.5, 0.4),
        )
    )
    
    

    cam_1 = Camera(
        RENDER_IMG_WIDTH, 
        RENDER_ASPECT_RATIO, 
        CAMERA_CENTER,
        CAMERA_LOOK_AT,
        samples = SAMPLES_PER_PIXEL,
        recursion_limit = RAY_BOUNCE_LIMIT,
        fov = FIELD_OF_VIEW,
        use_multiprocess = MULTIPROCESS
    )

    cam_1.render(scene, f"{SAVE_PATH}/{FILE_NAME}.png", silent=DRAW_SILENT)

# Protected Entry Point is Required for Multiprocessing
if __name__ == '__main__':
    main()