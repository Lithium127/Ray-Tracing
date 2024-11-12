from rtrace import Camera, Scene, Point3, SkyBox, Color, Assets, Mat
import random

# Protected Entry Point is Required for Multiprocessing
if __name__ == '__main__':
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
            # Assets.BVHNode(
            #     [
                    Assets.Sphere(
                        Point3(0, 0, -1),
                        0.5,
                        Mat.VectorShade(
                            # Color.average(
                            #     Color.RED(),
                            #     Color.BLUE()
                            # )
                        )
                    ),
                    Assets.Sphere(
                        Point3(-1.2, 0, -1),
                        0.5,
                        Mat.Metal(Color.GRAY())
                    ),
            #     ]
            # ),
            
            
        ],
        skybox = SkyBox.Lerp(
            Color(0.7, 0.5, 1),
            Color(0.9, 0.5, 0.4),
        )
    )
    
    

    cam_1 = Camera(
        512, 16/9, 
        Point3(0, 0, 1.5),
        Point3(0, 0, -1),
        samples = 1,
        recursion_limit = 8,
        fov = 60,
        use_multiprocess = False
    )

    cam_1.render(scene, "images/test.png", None, silent=False)