package main

import (
    "iastate-crim/src/routes"

	"github.com/gin-gonic/gin"
)

func main() {
	engine := gin.Default()
	routes.CreateRouter(engine)
	engine.Run()
//	http.HandleFunc("/roster.json", func(w http.ResponseWriter, r *http.Request) {
//		defer r.Body.Close()
//		if r.Method != http.MethodGet {
//			w.WriteHeader(404)
//			return
//		} else {
//
//			data, err := fs.ReadFile(os.DirFS("."), "roster.1724617329.060979.json")
//
//			if err != nil {
//				w.WriteHeader(500)
//				return
//			}
//
//			w.Header().Add("Content-Type", "application/json")
//			w.WriteHeader(http.StatusOK)
//			w.Write(data)
//		}
//	})
//	http.ListenAndServe(":8080", nil)
}
