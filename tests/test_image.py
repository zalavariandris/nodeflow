import nodeflow as nf
from pathlib import Path

if __name__ == '__main__':
    path = Path.cwd() / Path("tests/SMPTE_colorbars/SMPTE_colorbars_00001.jpg")
    filename = nf.Constant( str(path) )
    read = nf.image.Read(filename)
    blur = nf.image.GaussianBlur(read)

    ramp = nf.image.Ramp(size=(512,512))
    

    thumb_read = nf.image.Resize(blur, nf.Constant((128,128)))
    thumb_ramp = nf.image.Resize(ramp, nf.Constant((128,128)))

    blend = nf.image.Blend(thumb_read, thumb_ramp, nf.Constant(0.5))

    out = blend
    img = out.evaluate()

    import matplotlib.pyplot as plt
    plt.imshow(img)
    plt.show()