

# Welcome to `rtrace.py`
This is a project I have been working on for quite a long time, and I am excited to show you how it works and let you make your own renders.

- [Getting Started](#getting-started)
- [Adding Objects](#adding-objects)
- [Making a Render](#how-to-make-a-render)

![Good Render](images/skybox_test_1.png)

## Getting Started
This project has a ***code editor*** on the left hand side of the screen, this is where you will be placing assets in the scene and [rendering](#how-to-make-a-render). You can also see a ***large image*** in the upper right portion of your screen, this is the currently rendered scene view.

Finally, there is a small console bar at the bottom that will change when you start a render, so if something is moving there then the machine is working.


## Adding Objects
You can add assets to the scene with the following functions

```python
add_sphere(<center>, <radius>, <material>)
add_cube(<center>, <dimension>, <material>)
```

You can use IntelliSense to tell what each function requires, but the explainations are also below
> \<center> and \<dimension> are three digit `tuples`, for example (10, 10, 0.5)
>
> \<radius> is a `float`, ex: 1.0 or 0.25
>
> \<material> is a custom material implementation, but you can access common materials through the `Material` class

These are all common materials and their arguments, look at the functions to see what each means
```python
Material.default()
Material.metal(<color>, <fuzz>)
Material.image(<name>)
```


## How to make a render
To start the rendering process, press the `f5` key, located right above the `5` and `6` number keys on this keyboard.

You should notice the terminal section at the bottom of the screen start to move and change, meaning the rendering engine is working

![Basic Render](images/textured_skybox.png)