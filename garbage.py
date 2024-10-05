def pixbuf_from_array(z):
        " convert from numpy array to GdkPixbuf "
        z=z.astype('uint8')
        h,w,c=z.shape
        assert c == 3 or c == 4
        if hasattr(GdkPixbuf.Pixbuf,'new_from_bytes'):
            Z = GLib.Bytes.new(z.tobytes())
            return GdkPixbuf.Pixbuf.new_from_bytes(Z, GdkPixbuf.Colorspace.RGB, c==4, 8, w, h, w*c)
        return GdkPixbuf.Pixbuf.new_from_data(z.tobytes(),  GdkPixbuf.Colorspace.RGB, c==4, 8, w, h, w*c, None, None)

    def array_from_pixbuf(self, p):
        " convert from GdkPixbuf to numpy array"
        import numpy

        w,h,c,r=(p.get_width(), p.get_height(), p.get_n_channels(), p.get_rowstride())
        assert p.get_colorspace() == GdkPixbuf.Colorspace.RGB
        assert p.get_bits_per_sample() == 8
        if  p.get_has_alpha():
            assert c == 4
        else:
            assert c == 3
        assert r >= w * c
        a=numpy.frombuffer(p.get_pixels(),dtype=numpy.uint8)
        if a.shape[0] == w*c*h:
            return a.reshape( (h, w, c) )
        else:
            b=numpy.zeros((h,w*c),'uint8')
            for j in range(h):
                b[j,:]=a[r*j:r*j+w*c]
            return b.reshape( (h, w, c) )

# EOF
