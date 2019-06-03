
%struct.c = type {i32}

define %struct.c @func.func(i32 %a, i32 %b) {
    %a.ptr = alloca i32
    %b.ptr = alloca i32
    store i32 %a, i32* %a.ptr
    store i32 %b, i32* %b.ptr
    %aa.ptr = alloca %struct.c
    %aa.1 = load %struct.c, %struct.c* %aa.ptr
    ret %struct.c %aa.1
}

define i32 @main() {
    br label %lab.0
lab.0:
    %d.ptr = alloca i32
    %buffer2 = add i32 1, 1
    store i32 %buffer2, i32* %d.ptr
    %d.3 = load i32, i32* %d.ptr
    %buffer4 = icmp eq i32 %d.3, 2
    br i1 %buffer4, label %lab.2, label %lab.3
lab.2:
    store i32 3, i32* %d.ptr
    %d.5 = load i32, i32* %d.ptr
    %buffer6 = icmp ne i32 %d.5, 3
    br i1 %buffer6, label %lab.4, label %lab.5
lab.4:
    br label %lab.2
    br label %lab.6
lab.5:
    br label %lab.7
lab.7:
    br label %lab.3
    br label %lab.6
lab.8:
    br label %lab.6
lab.6:
    br i1 %buffer4, label %lab.2, label %lab.3
lab.3:
    br label %lab.1
    br i1 1, label %lab.0, label %lab.1
lab.1:
    %a.ptr = alloca i8*
    store i8* getelementptr inbounds ([4 x i8], [4 x i8]* @.str.1, i32 0, i32 0), i8** %a.ptr
    %b.ptr = alloca double
    store double 2.2, double* %b.ptr
    %buffer7 = load double, double* %b.ptr
    %buffer8 = load double, double* %b.ptr
    %buffer9 = load double, double* %b.ptr
    %buffer10 = load double, double* %b.ptr
    %buffer11 = load double, double* %b.ptr
    %buffer12 = getelementptr inbounds [18 x i8], [18 x i8]* @.str.3, i32 0, i32 0 
    call i32 (i8*, ...) @printf(i8* %buffer12, double %buffer7, double %buffer8, double %buffer9, double %buffer10, double %buffer11)
    ret i32 0
}

declare i32 @printf(i8*, ...)
@.str.1 = private unnamed_addr constant [4 x i8] c"123\00", align 1
@.str.2 = private unnamed_addr constant [2 x i8] c" \00", align 1
@.str.3 = private unnamed_addr constant [18 x i8] c"%lf %lf%lf%lf%lf\0A\00", align 1
