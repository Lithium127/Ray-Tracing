from rtrace import Camera, Scene, Point3, Vector3, SkyBox, Color, Assets, Mat, Texture


""" =========== """
"""  CONSTANTS  """
""" =========== """

# Image Information
RENDER_IMG_WIDTH    = 1024
RENDER_ASPECT_RATIO = 16/9
SAVE_PATH = "images"
FILE_NAME = "utah_teapot_8samp"

# Rendering Quality
SAMPLES_PER_PIXEL = 8
RAY_BOUNCE_LIMIT  = 16

# Camera Data
CAMERA_CENTER  = Point3(2, 3, 3.5)
CAMERA_LOOK_AT = Point3(0, 1, 0)
FIELD_OF_VIEW  = 90
DRAW_SILENT    = False
MULTIPROCESS   = True



def main():
    scene = Scene(
        # [
        #     Assets.Sphere(
        #         Point3(0, 0, -1),
        #         0.5,
        #         Mat.Metal(
        #             Color.GRAY()
        #         )
        #     ),
        #     Assets.Sphere(
        #         Point3(1.1, 0, -1),
        #         0.5,
        #         Mat.Dielectric.Glass(
        #             Color.WHITE()
        #         )
        #     ),
        #     Assets.Triangle(
        #         vertices=(
        #             Point3(-1, 0, -1),
        #             Point3(-1, 1, -1),
        #             Point3(-2, 0, -1),
        #         ),
        #         mat=Mat.Lambertian(Texture.ImageMap("textures/ArtificalTexture.png"))
        #     ),
        #     Assets.Sphere(
        #         Point3(0, -100.5, 0),
        #         100,
        #         Mat.Lambertian(Color.GRAY())
        #     )
        # ],
        [
            Assets.Model.from_obj(
                "models/utah_teapot.obj",
                mat = Mat.Metal(
                    Color.GRAY(),
                    0.2
                )
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