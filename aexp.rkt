#lang racket

;; an Op is (anyof '+ '*)
;; an AExp is (anyof Num (cons Op (listof AExp)))

(define op-table
  (list (list '+ +)
        (list '* *)))
        
;; my-reverse: (listof X) -> (listof X)
(define my-reverse
  (lambda (lox)
    (foldl cons '() lox)))

;; look-up: Sym AL -> (anyof (Num Num -> Num) false)
(define look-up
  (lambda (key al)
    (cond [(empty? al) false]
          [(symbol=? key (first (first al))) (second (first al))]
          [else (look-up key (rest al))])))
          
;; my-eval: AExp -> Num
(define my-eval
  (lambda (aexp)
    (cond [(number? aexp) aexp]
          [else (my-apply (look-up (first aexp) op-table)
                          (rest aexp))])))
          
;; my-apply: (Num Num -> Num) (listof AExp) -> Num
(define my-apply
  (lambda (op args)
    (cond [(empty? args) (op)]
          [else (op (my-eval (first args))
                    (my-apply op (rest args)))])))

;; steps/list: Op (listof Num) (listof AExp) -> (listof AExp)
(define steps/list
  (lambda (op prefix args)
    (cond [(empty? args) (list (my-apply (look-up op op-table) prefix))]
          [(number? (first args)) (steps/list op (cons (first args) prefix) (rest args))]
          [else (append (map (lambda (loaexp) (append (cons op (my-reverse prefix))
                                                      (list loaexp)
                                                      (rest args)))
                             (steps (first args)))
                        (steps/list op (cons (my-eval (first args)) prefix) (rest args)))])))

;; steps: AExp -> (listof AExp)
(define steps
  (lambda (aexp)
    (cond [(number? aexp) (list aexp)]
          [else (steps/list (first aexp) '() (rest aexp))])))

(display "exp: ")
(steps (read))
