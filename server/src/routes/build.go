package routes

import (
	routes_inmates "iastate-crim/src/routes/inmates"
	"github.com/gin-gonic/gin"
)

func CreateRouter(r *gin.Engine) {
	r_inmates := r.Group("/inmates"); {
		r_inmates.GET("/", routes_inmates.GET)
	}
	r.GET("/", GET)
}
