from rtrace import Camera, Scene, Point3, Vector3, SkyBox, Color, Assets, Mat


""" =========== """
"""  CONSTANTS  """
""" =========== """

# Image Information
RENDER_IMG_WIDTH    = 1024
RENDER_ASPECT_RATIO = 1
SAVE_PATH = "images"
FILE_NAME = "false_cornell"

# Rendering Quality
SAMPLES_PER_PIXEL = 256
RAY_BOUNCE_LIMIT  = 16

# Camera Data
CAMERA_CENTER  = Point3(278, 278, -800)
CAMERA_LOOK_AT = Point3(278, 278, 0)
FIELD_OF_VIEW  = 38
DRAW_SILENT    = False
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
    
    white = Mat.Lambertian(Color(.71, .71, .71))
    green = Mat.Lambertian(Color(.12, .45, .15))
    red   = Mat.Lambertian(Color(.65, .05, .05))
    light = Mat.DiffuseLight(15)
    
    scene = Scene(
        [
            Assets.HittableList(
                [
                    Assets.Quad(Point3(555, 0, 0), Vector3(0, 555, 0), Vector3(0, 0, 555), green),
                    Assets.Quad(Point3(0, 0, 0), Vector3(0, 555, 0), Vector3(0, 0, 555), red),
                    Assets.Quad(Point3(343, 554, 332), Vector3(-130,0,0), Vector3(0,0,-105), light),
                    Assets.Quad(Point3(0, 0, 0), Vector3(555, 0, 0), Vector3(0, 0, 555), white),
                    Assets.Quad(Point3(555, 555, 555), Vector3(-555, 0, 0), Vector3(0, 0,-555), white),
                    Assets.Quad(Point3(0, 0, 555), Vector3(555, 0, 0), Vector3(0, 555, 0), white)
                ],
                use_bvh=False
            ),
            Assets.Sphere(
                Point3(170, 125, 200),
                125,
                Mat.Dielectric.Glass()
            ),
            Assets.Quad.Cube(
                Point3(295, 0, 295),
                Point3(460, 330, 460),
                Mat.Lambertian(Color(0.5, 0.9, 0.9))
            )
        ],
        skybox = SkyBox.Mono(
            Color.BLACK()
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