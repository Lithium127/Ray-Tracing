from rtrace import Camera, Scene, Point3, Vector3, SkyBox, Color, Assets, Mat


""" =========== """
"""  CONSTANTS  """
""" =========== """

# Image Information
RENDER_IMG_WIDTH    = 1024
RENDER_ASPECT_RATIO = 16/9
SAVE_PATH = "images"
FILE_NAME = "quad_test"

# Rendering Quality
SAMPLES_PER_PIXEL = 1
RAY_BOUNCE_LIMIT  = 8

# Camera Data
CAMERA_CENTER  = Point3(1, 1.5, 1.5)
CAMERA_LOOK_AT = Point3(0, 0, -1)
FIELD_OF_VIEW  = 60
DRAW_SILENT    = True
MULTIPROCESS   = True




def main():
    
    a = [
        Assets.Sphere(
            Point3(x % 10, -0.8, x // 10),
            0.2,
            Mat.Lambertian(
                Color.WHITE()
            )
        )
        for x in range(10 * 10)
    ]
    
    scene = Scene(
        [
            # Ground object
            Assets.Sphere(
                Point3(0, -100.5, -1), 
                100, 
                Mat.Lambertian(Color.GRAY()),
            ),
            Assets.Quad.Cube(
                Point3(0.5, 0, -0.5),
                Point3(-0.5, 1, -1.5),
                Mat.Metal(
                    Color.average(
                        Color.GRAY(),
                        Color.BLUE()
                    ), 
                    0.1
                )
            )
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