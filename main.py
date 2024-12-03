from rtrace import Camera, Scene, Point3, Vector3, SkyBox, Color, Assets, Mat, Texture


""" =========== """
"""  CONSTANTS  """
""" =========== """

# Image Information
RENDER_IMG_WIDTH    = 512
RENDER_ASPECT_RATIO = 16/9
SAVE_PATH = "images"
FILE_NAME = "checker_board"

# Rendering Quality
SAMPLES_PER_PIXEL = 1
RAY_BOUNCE_LIMIT  = 16

# Camera Data
CAMERA_CENTER  = Point3(0, 0, 1)
CAMERA_LOOK_AT = Point3(0, 0, -1.5)
FIELD_OF_VIEW  = 90
DRAW_SILENT    = True
MULTIPROCESS   = True



def main():
    
    scene = Scene(
        [
            Assets.Sphere(
                Point3(0, 0, -1),
                0.5,
                Mat.Metal(
                    Color.GRAY()
                )
            ),
            Assets.Sphere(
                Point3(1.1, 0, -1),
                0.5,
                Mat.Dielectric.Glass(
                    Color.WHITE()
                )
            ),
            Assets.Sphere(
                Point3(0, -100.5, 0),
                100,
                Mat.Lambertian(Color.GRAY())
            )
        ],
        skybox = SkyBox.Textured(
            "textures/brown_photostudio_02.jpg", 
            (90, 0),
            0.5
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