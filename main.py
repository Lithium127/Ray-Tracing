from rtrace import Camera, Scene, Point3, SkyBox, Color, Assets, Mat


# Protected Entry Point is Required for Multiprocessing
if __name__ == '__main__':
    scene = Scene(
        [
            Assets.Sphere(
                Point3(0, 0, -1), 
                0.5, 
                Mat.VectorShade()
            ),
            Assets.Sphere(
                Point3(1, 0, -1), 
                0.5, 
                Mat.Metal(Color.GRAY())
            ),
            
            Assets.Sphere(
                Point3(-1, 0, -1),
                0.5,
                Mat.Dielectric(1.0/1.5, Color.GREEN())
            ),
            
            Assets.Sphere(
                Point3(0, -100.5, -1), 
                100, 
                Mat.Lambertian(Color.GRAY())
            )
        ],
        skybox = SkyBox.Lerp(
            Color(0.7, 0.5, 1),
            Color(0.9, 0.5, 0.4),
        )
    )

    cam_1 = Camera(
        512, 16/9, 
        Point3(-2, 2, 1),
        Point3(0, 0, -1),
        samples = 8,
        recursion_limit = 16,
        fov = 20,
        use_multiprocess = False
    )

    cam_1.render(scene, "images/test.png", None, silent=False)