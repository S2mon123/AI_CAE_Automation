#include "udf.h"
#include "math.h"

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

DEFINE_PROFILE(moving_heat_source_sinusoidal, thread, position)
{
    real time = CURRENT_TIME;
    real xc[ND_ND];
    real radius;
    real heat_flux;

    /* User parameters in SI units. Tune Q for validation vs. calibrated runs. */
    real Q = 1000.0;
    real v = 0.003;
    real A = 0.003;
    real freq = 2.0;
    real r_beam = 0.003;
    real eta = 0.75;

    /* Normalized Gaussian surface heat flux. Verify sign convention locally. */
    real q_max = 3.0 * eta * Q / (M_PI * r_beam * r_beam);

    real x_center = v * time;
    real y_center = A * sin(2.0 * M_PI * freq * time);

    face_t face_id;

    begin_f_loop(face_id, thread)
    {
        F_CENTROID(xc, face_id, thread);
        radius = sqrt((xc[0] - x_center) * (xc[0] - x_center)
                    + (xc[1] - y_center) * (xc[1] - y_center));

        heat_flux = q_max * exp(-3.0 * radius * radius / (r_beam * r_beam));
        F_PROFILE(face_id, thread, position) = heat_flux;
    }
    end_f_loop(face_id, thread)
}
